import asyncio
import json
import sys
import os
import random
import re
import threading

from discord.ext import commands, tasks


def update():
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

with open(resource_path("trivia.json")) as file:
    trivia_dict = json.load(file)


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chance = config_dict["trivia_correct_chance"]

    async def cog_load(self):
        self.trivia.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or config_dict["commands"]["state"] is False or config_dict["commands"]["trivia"] is False:
            return

        for embed in message.embeds:
            try:
                if embed.to_dict()["fields"][0]["name"] == "Difficulty":
                    category = embed.to_dict()["fields"][1]["value"][1:-1]
                    question = re.search("\*\*(.*?)\*\*", embed.to_dict()["description"]).group(1)
                    try:
                        answer = trivia_dict[category][question]
                    except:
                        await message.components[0].children[0].click()
                        return
                    if random.random() <= self.chance:
                        if message.components[0].children[0].label == answer:
                            await message.components[0].children[0].click()
                        elif message.components[0].children[1].label == answer:
                            await message.components[0].children[1].click()
                        elif message.components[0].children[2].label == answer:
                            await message.components[0].children[2].click()
                        elif message.components[0].children[3].label == answer:
                            await message.components[0].children[3].click()
                    else:
                        if message.components[0].children[0].label != answer:
                            await message.components[0].children[0].click()
                        else:
                            await message.components[0].children[1].click()
            except KeyError:
                pass

    @tasks.loop(seconds=15)
    async def trivia(self):
        if config_dict["commands"]["trivia"] is True and config_dict["commands"]["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371309510698]):
                await cmd()
                return


async def setup(bot):
    await bot.add_cog(Trivia(bot))
