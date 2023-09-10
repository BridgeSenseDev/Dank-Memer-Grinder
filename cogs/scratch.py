import asyncio
import random

from discord.ext import commands


class Scratch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "scratch"):
            return

        self.bot.log("Solving Scratch", "yellow")

        for _ in range(4):
            await asyncio.sleep(random.uniform(0.4, 0.9))
            await self.bot.click(message, random.randint(0, 4), random.randint(0, 2))

        await asyncio.sleep(0.5)
        await self.bot.click(message, 4, 3)
        self.bot.log("Solved Scratch", "green")


async def setup(bot):
    await bot.add_cog(Scratch(bot))
