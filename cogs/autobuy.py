import asyncio
import re

from discord.ext import commands


class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_message = None

    async def shop_buy(self, item, count=1):
        while not self.shop_message:
            await self.bot.sub_send("shop", "view")
            await asyncio.sleep(1)

        found = False
        while not found:
            for row in range(1, 3):
                for col, button in enumerate(
                    self.shop_message.components[row].children
                ):
                    if item in button.label.lower():
                        await self.bot.click(self.shop_message, row, col)

                        modal = await self.bot.wait_for("modal")
                        modal.components[0].children[0].answer(str(count))

                        await modal.submit()
                        return

            await self.bot.click(self.shop_message, 3, 2)
            await asyncio.sleep(0.3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and self.bot.state:
            for embed in message.embeds:
                embed = embed.to_dict()
                # Buy lifesavers
                try:
                    if (
                        embed["title"] == "Your lifesaver protected you!"
                        and self.bot.config_dict["autobuy"]["lifesavers"]["state"]
                    ):
                        remaining = int(
                            re.search(
                                "have (.*?)x Life Saver",
                                message.components[0].children[0].label,
                            ).group(1)
                        )
                        required = int(
                            self.bot.config_dict["autobuy"]["lifesavers"]["amount"]
                        )
                        if remaining < required:
                            channel = await message.author.create_dm()
                            await self.bot.send(
                                "withdraw",
                                channel,
                                amount=str((required - remaining) * 200000),
                            )
                            await self.shop_buy("saver", required - remaining)
                            self.bot.log(
                                f"Bought {required - remaining} Lifesavers",
                                "yellow",
                            )
                            return
                except KeyError:
                    pass

                # Confirm purchase
                try:
                    if (
                        embed["title"] == "Pending Confirmation"
                        and self.bot.config_dict["autobuy"]["lifesavers"]["state"]
                    ):
                        await self.bot.click(message, 0, 1)
                except KeyError:
                    pass

        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

        if message.interaction and message.interaction.name == "shop view":
            print("new message")
            self.shop_message = message

        for embed in message.embeds:
            embed = embed.to_dict()
            # Shovel
            try:
                if (
                    "You don't have a shovel, you need to go buy one."
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["shovel"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("shovel", 1)
                    self.bot.log(
                        f"Bought Shovel",
                        "yellow",
                    )
            except KeyError:
                pass

            # Fishing pole
            try:
                if (
                    "You don't have a fishing pole, you need to go buy one"
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["fishing"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("pole", 1)
                    self.bot.log(
                        f"Bought Shovel",
                        "yellow",
                    )
            except KeyError:
                pass

            # Hunting rifle
            try:
                if (
                    "You don't have a hunting rifle, you need to go buy one."
                    in embed["description"]
                    and self.bot.config_dict["autobuy"]["rifle"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.shop_buy("rifle", 1)
                    self.bot.log(
                        f"Bought Shovel",
                        "yellow",
                    )
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Autobuy(bot))
