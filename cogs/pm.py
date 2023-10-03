import asyncio
import random
import time

from discord.ext import commands


class Pm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "pm"):
            return

        platforms = self.bot.config_dict["commands"]["pm"]["platforms"]
        platform = random.choice(platforms)

        if not message.components[0].children[0].options[platform].default:
            await self.bot.select(message, 0, 0, platform)
            await asyncio.sleep(0.3)
        await self.bot.click(message, 2, 0)
        self.bot.last_ran["pm"] = time.time()

        await asyncio.sleep(1)
        embed = message.embeds[0].to_dict()
        if "cannot post another meme for another 3 minutes" in embed["description"]:
            self.bot.last_ran["pm"] += 200


async def setup(bot):
    await bot.add_cog(Pm(bot))
