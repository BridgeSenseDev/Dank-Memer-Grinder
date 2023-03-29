import random

from discord.ext import commands

priority = []
second_priority = []
avoid = []


class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "crime"):
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
    await bot.add_cog(Crime(bot))
