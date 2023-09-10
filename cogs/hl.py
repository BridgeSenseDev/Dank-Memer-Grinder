import re
import time

from discord.ext import commands


class Hl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "hl"):
            return

        embed = message.embeds[0].to_dict()
        num = int(re.search(r"\*\*(.*?)\*\*", embed["description"])[1].title())
        if num >= 50:
            await self.bot.click(message, 0, 0)
        else:
            await self.bot.click(message, 0, 2)
        self.bot.last_ran["hl"] = time.time()


async def setup(bot):
    await bot.add_cog(Hl(bot))
