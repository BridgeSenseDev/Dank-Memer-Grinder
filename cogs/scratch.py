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

        self.bot.pause = True
        self.bot.log("Solving Scratch", "yellow")

        coordinates = [(x, y) for x in range(5) for y in range(3)]
        random.shuffle(coordinates)

        for _ in range(4):
            await asyncio.sleep(random.uniform(0.4, 0.9))
            x, y = coordinates.pop()
            await self.bot.click(message, x, y)

        await asyncio.sleep(0.3)
        await self.bot.click(message, 4, 3)
        self.bot.log("Solved Scratch", "green")
        self.bot.pause = False


async def setup(bot):
    await bot.add_cog(Scratch(bot))
