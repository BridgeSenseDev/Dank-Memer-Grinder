import random

from discord.ext import commands

priority = ["hacking", "tax evasion", "treason"]
second_priority = ["dui", "bank robbing", "eating a hot dog sideways", "murder"]
avoid = ["arson", "fraud", "trespassing"]


class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "crime"):
            return

        children = message.components[0].children
        random.shuffle(children)
        for count, button in enumerate(children):
            if button.label.lower() in priority:
                await self.bot.click(message, 0, count)
                return
        for count, button in enumerate(children):
            if button.label.lower() in second_priority:
                await self.bot.click(message, 0, count)
                return
        for count, button in enumerate(children):
            if button.label.lower() not in avoid:
                await self.bot.click(message, 0, count)
                return


async def setup(bot):
    await bot.add_cog(Crime(bot))
