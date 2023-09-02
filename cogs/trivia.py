import asyncio
import json
import os
import random
import re
import sys

import discord
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
        self.chance = self.bot.config_dict["commands"]["trivia"][
            "trivia_correct_chance"
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "trivia"):
            return

        embed = message.embeds[0].to_dict()
        category = embed["fields"][1]["value"]
        question = re.search(r"\*\*(.*?)\*\*", embed["description"])[1]
        try:
            answer = trivia_dict[category][question]
        except KeyError:
            await self.bot.click(message, 0, random.randint(0, 3))
            await asyncio.sleep(0.5)
            for button in message.components[0].children:
                if button.style == discord.ButtonStyle.success:
                    trivia_dict[category][question] = button.label
                    with open(
                        resource_path("resources/trivia.json"),
                        "w",
                        encoding="utf-8",
                    ) as trivia_file:
                        json.dump(trivia_dict, trivia_file, indent=4)
                    return

        if random.random() <= self.chance:
            for count, i in enumerate(message.components[0].children):
                if i.label == answer:
                    await self.bot.click(message, 0, count)
        elif message.components[0].children[0].label == answer:
            await self.bot.click(message, 0, 1)

        else:
            await self.bot.click(message, 0, 0)


async def setup(bot):
    await bot.add_cog(Trivia(bot))
