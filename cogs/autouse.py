import asyncio
import re
import time

from discord.ext import commands, tasks


class Autouse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_ran = {}
        self.autouse.start()

    @tasks.loop(seconds=0.05)
    async def autouse(self):
        if not self.bot.state:
            await asyncio.sleep(1)
            return

        for autouse in self.bot.config_dict["autouse"]:
            if autouse in ["state", "hide_disabled"]:
                continue

            if autouse not in self.last_ran:
                if (
                    self.bot.config_dict["autouse"]["state"]
                    and self.bot.config_dict["autouse"][autouse]["state"]
                ):
                    user = await self.bot.fetch_user(270904126974590976)
                    channel = await user.create_dm()
                    await self.bot.send(
                        "use",
                        channel,
                        item=autouse.replace("_", " ").title(),
                    )
                    self.last_ran[autouse] = time.time()
                    self.bot.log(
                        f"Used {autouse.replace('_', '' '').title()}", "yellow"
                    )
                    await asyncio.sleep(10)
                    continue
                self.last_ran[autouse] = 0
                continue

            if (
                time.time() - self.last_ran[autouse] < 1800
                or not self.bot.config_dict["autouse"]["state"]
                or not self.bot.config_dict["autouse"][autouse]["state"]
            ):
                await asyncio.sleep(5)
                continue
            self.last_ran[autouse] = time.time()
            user = await self.bot.fetch_user(270904126974590976)
            channel = await user.create_dm()
            await self.bot.send(
                "use",
                channel,
                item=autouse.replace("_", " ").title(),
            )
            self.bot.log(f"Used {autouse.replace('_', '' '').title()}", "yellow")
            await asyncio.sleep(10)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.guild is None
            and message.author.id == 270904126974590976
            and self.bot.state is True
        ):
            for embed in message.embeds:
                embed = embed.to_dict()
                # Buy lifesavers
                try:
                    if embed["title"] == "Item Expiration":
                        for autouse in self.bot.config_dict["autouse"]:
                            if (
                                autouse.replace("_", " ")
                                in embed["description"].lower()
                                and self.bot.config_dict["autouse"][autouse]["state"]
                            ):
                                channel = await message.author.create_dm()
                                await self.bot.send(
                                    "use",
                                    channel,
                                    item=autouse.replace("_", " ").title(),
                                )
                                self.bot.log(
                                    f"Used {autouse.replace('_', '' '').title()}",
                                    "yellow",
                                )
                                return
                except KeyError:
                    pass


async def setup(bot):
    await bot.add_cog(Autouse(bot))
