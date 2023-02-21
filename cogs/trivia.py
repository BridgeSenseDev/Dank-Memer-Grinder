import json
import os
import random
import re
import sys

from discord.ext import commands


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


with open(resource_path("resources/trivia.json")) as file:
    trivia_dict = json.load(file)


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chance = self.bot.config_dict["trivia_correct_chance"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or self.bot.state is False
            or self.bot.config_dict["commands"]["trivia"] is False
        ):
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            try:
                if embed["fields"][0]["name"] == "Difficulty":
                    category = embed["fields"][1]["value"][1:-1]
                    question = re.search("\*\*(.*?)\*\*", embed["description"]).group(1)
                    try:
                        answer = trivia_dict[category][question]
                    except KeyError:
                        await self.bot.click(message, 0, random.randint(0, 3))
                        return
                    if random.random() <= self.chance:
                        for count, i in enumerate(message.components[0].children):
                            if i.label == answer:
                                await self.bot.click(message, 0, count)
                    else:
                        if message.components[0].children[0].label != answer:
                            await self.bot.click(message, 0, 0)
                        else:
                            await self.bot.click(message, 0, 1)
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Trivia(bot))
