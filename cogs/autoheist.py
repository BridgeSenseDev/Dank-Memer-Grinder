import asyncio
import contextlib
import random

from discord.ext import commands


class AutoHeist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        if self.bot.global_config_dict["autoheist"]:
            self.bot.log("Heist Channels:", "yellow")
            for channel in self.bot.global_config_dict["autoheist"]:
                self.bot.log(f"{channel}", "yellow")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.state:
            return
        for autoheist in self.bot.global_config_dict["autoheist"]:
            if message.channel.id != int(autoheist):
                continue
            with contextlib.suppress(KeyError):
                embed = message.embeds[0].to_dict()
                if (
                    " is starting a bank robbery" in embed["title"]
                    and str(self.bot.user) not in embed["title"]
                    and not message.components[0].children[0].disabled
                ):
                    await asyncio.sleep(random.uniform(0.6, 1.2))
                    await self.bot.click(message, 0, 0)
                    self.bot.log(
                        f"Joined heist in {message.channel.guild.name}", "green"
                    )
                    return


async def setup(bot):
    await bot.add_cog(AutoHeist(bot))
