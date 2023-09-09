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

        self.bot.log("doing scratch", "yellow")
        self.bot.state = False

        for _ in range(4):
            await asyncio.sleep(random.uniform(0.4, 0.9))
            await self.bot.click(message, random.randint(0, 4), random.randint(0, 2))
            await asyncio.sleep(random.uniform(0.1, 0.2))
            self.bot.log("end", "yellow")

        self.bot.log("end bttn", "yellow")
        await self.bot.click(message, 4, 3)
        self.bot.log("end bttn(2)", "yellow")
        self.bot.state = True


async def setup(bot):
    await bot.add_cog(Scratch(bot))