import asyncio
import random

from discord.ext import commands


class Pm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "pm"):
            return

        await self.bot.select(message, 0, 0, random.randint(0, 3))
        await asyncio.sleep(0.3)
        await self.bot.select(message, 1, 0, random.randint(0, 4))
        await asyncio.sleep(0.3)
        await self.bot.click(message, 2, 0)


async def setup(bot):
    await bot.add_cog(Pm(bot))
