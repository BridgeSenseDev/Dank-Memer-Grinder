import random

from discord.ext import commands

priority = [
    "phoenix pits",
    "aeradella's home",
    "soul's chamber",
    "god's own place",
    "dog",
    "grass",
    "air",
    "kitchen",
]
second_priority = ["who asked", "fridge"]
avoid = ["area51", "bank"]


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "search"):
            return

        children = message.components[0].children
        random.shuffle(children)
        for i in children:
            if i.label in priority:
                await self.bot.click(message, 0, children.index(i))
                return
            if i.label in second_priority:
                await self.bot.click(message, 0, children.index(i))
                return
            if i.label not in avoid:
                await self.bot.click(message, 0, children.index(i))
                return


async def setup(bot):
    await bot.add_cog(Search(bot))
