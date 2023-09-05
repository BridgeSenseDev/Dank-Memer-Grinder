import asyncio
import contextlib
import re

from discord.ext import commands


class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_message = None

    async def shop_buy(self, item, count=1):
        await self.bot.sub_send("shop", "view")

        def check(msg):
            return msg.embeds[0].to_dict()["title"] == "Dank Memer Shop"

        message = await self.bot.wait_for("message", check=check)
        if message.components[3].children[1].emoji.id == 1105833876032606350:
            await self.bot.click(message, 3, 1)
            await asyncio.sleep(0.5)

        found = False
        while not found:
            for row in range(1, 3):
                for col, button in enumerate(message.components[row].children):
                    if item in button.label.lower():
                        await self.bot.click(message, row, col)

                        modal = await self.bot.wait_for("modal")
                        modal.components[0].children[0].answer(str(count))

                        await modal.submit()
                        return

            await self.bot.click(message, 3, 2)
            await asyncio.sleep(0.3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and self.bot.state:
            for embed in message.embeds:
                embed = embed.to_dict()
                # Buy lifesavers
                with contextlib.suppress(KeyError):
                    if (
                        embed["title"] == "Your lifesaver protected you!"
                        and self.bot.config_dict["autobuy"]["lifesavers"]["state"]
                    ):
                        remaining = int(
                            re.search(
                                "have (.*?)x Life Saver",
                                message.components[0].children[0].label,
                            )[1]
                        )
                        required = int(
                            self.bot.config_dict["autobuy"]["lifesavers"]["amount"]
                        )
                        if remaining < required:
                            await self.bot.send(
                                "withdraw",
                                amount=str((required - remaining) * 200000),
                            )
                            await self.shop_buy("saver", required - remaining)
                            self.bot.log(
                                f"Bought {required - remaining} Lifesavers",
                                "yellow",
                            )
                            return
                # Confirm purchase
                with contextlib.suppress(KeyError):
                    if (
                        embed["title"] == "Pending Confirmation"
                        and self.bot.config_dict["autobuy"]["lifesavers"]["state"]
                    ):
                        await self.bot.click(message, 0, 1)
        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            # Shovel
            with contextlib.suppress(KeyError):
                if (
                    "You don't have a shovel, you need to go buy one."
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["shovel"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("shovel", 1)
                    self.bot.log("Bought Shovel", "yellow")
            # Fishing pole
            with contextlib.suppress(KeyError):
                if (
                    "You don't have a fishing pole, you need to go buy one"
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["fishing"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("pole", 1)
                    self.bot.log("Bought Shovel", "yellow")
            # Hunting rifle
            with contextlib.suppress(KeyError):
                if (
                    "You don't have a hunting rifle, you need to go buy one."
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["rifle"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("rifle", 1)
                    self.bot.log("Bought Shovel", "yellow")


async def setup(bot):
    await bot.add_cog(Autobuy(bot))
