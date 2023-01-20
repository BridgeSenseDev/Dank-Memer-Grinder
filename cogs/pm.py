import asyncio
import random

from discord.ext import commands


class Pm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or self.bot.config_dict[self.bot.account_id]["commands"]["pm"] is False
            or self.bot.config_dict[self.bot.account_id]["state"] is False
        ):
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            try:
                if "Meme Posting Session" in embed["author"]["name"]:
                    await asyncio.sleep(0.7)
                    await self.bot.select(message, 0, 0, random.randint(0, 3))
                    await asyncio.sleep(0.7)
                    await self.bot.select(message, 1, 0, random.randint(0, 4))
                    await asyncio.sleep(0.7)
                    await self.bot.click(message, 2, 0)
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Pm(bot))
