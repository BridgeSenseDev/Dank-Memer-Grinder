import threading
import json
import random
import asyncio

from discord.ext import commands, tasks

search_priority = ["phoenix pits", "aeradella's home", "soul's chamber", "god's own place", "dog", "grass", "air",
                   "kitchen"]
second_search_priority = ["who asked", "fridge"]
search_avoid = ["area51", "bank"]


def update():
    global commands_dict
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
    with open("commands.json", "r") as commands_file:
        commands_dict = json.load(commands_file)


update()


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.search.start()

    @tasks.loop(seconds=42)
    async def search(self):
        if commands_dict["search"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371267579935]):
                await cmd()
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or commands_dict["state"] is False or commands_dict["search"] is False:
            return

        for embed in message.embeds:
            try:
                if "to search?" in embed.to_dict()["description"]:
                    for i in message.components[0].children:
                        if i.label in search_priority:
                            await i.click()
                            return
                    for i in message.components[0].children:
                        if i.label in second_search_priority:
                            await i.click()
                            return
                    for i in message.components[0].children:
                        if i.label not in search_avoid:
                            await i.click()
                            return
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Search(bot))
