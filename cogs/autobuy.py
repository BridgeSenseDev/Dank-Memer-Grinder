import re
from discord.ext import commands

class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and self.bot.state:
            for embed in message.embeds:
                embed = embed.to_dict()

                # Buy lifesavers
                try:
                    if (
                        embed["title"] == "Your lifesaver protected you!"
                        and self.bot.config_dict.get("autobuy", {}).get("lifesavers", {}).get("state")
                    ):
                        remaining = int(
                            re.search(
                                r"have (.*?)x Life Saver",
                                message.components[0].children[0].label,
                            ).group(1)
                        )
                        required = int(
                            self.bot.config_dict.get("autobuy", {}).get("lifesavers", {}).get("amount")
                        )
                        if remaining < required:
                            price = await self.get_price_from_shop()

                            if price is None:
                                fallback_price = 250000
                                self.bot.log("Failed to retrieve the price. Using fallback price.", "red")
                                price = fallback_price

                            total_amount = await self.get_total_amount()

                            if price <= total_amount:
                                wallet_amount = await self.get_wallet_amount()
                                if price <= wallet_amount:
                                    # Buy lifesavers
                                    await self.bot.sub_send(
                                        "shop",
                                        "buy",
                                        channel,
                                        item="Life Saver",
                                        quantity=str(required),
                                    )
                                    self.bot.log(f"Bought {required} Lifesavers.", "yellow")
                                else:
                                    # Withdraw funds
                                    withdrawal_amount = price - wallet_amount
                                    await self.bot.send("withdraw", channel, str(withdrawal_amount))

                                    # Buy lifesavers
                                    await self.bot.sub_send(
                                        "shop",
                                        "buy",
                                        channel,
                                        item="Life Saver",
                                        quantity=str(required),
                                    )
                                    self.bot.log(f"Withdrew ⏣{withdrawal_amount} and bought {required} Lifesavers.", "yellow")
                            else:
                                self.bot.log("Insufficient funds to buy Lifesavers.", "red")
                        else:
                            self.bot.log("Already have enough Lifesavers. Skipping purchase.", "green")
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

                # Shovel
                try:
                    if (
                        "You don't have a shovel, you need to go buy one."
                        in embed["description"]
                        and self.bot.config_dict["autobuy"]["shovel"]
                    ):
                        await self.bot.send("withdraw", amount="35k")
                        await self.bot.sub_send("shop", "buy", item="Shovel", quantity="1")
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
                        await self.bot.sub_send(
                            "shop", "buy", item="Fishing Pole", quantity="1"
                        )
                        self.bot.log(
                            f"Bought Fishing Pole",
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
                        await self.bot.sub_send(
                            "shop", "buy", item="Hunting Rifle", quantity="1"
                        )
                        self.bot.log(
                            f"Bought Hunting Rifle",
                            "yellow",
                        )
                except KeyError:
                    pass

        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

        for embed in message.embeds:
            embed = embed.to_dict()

    async def get_price_from_shop(self):
        await self.bot.sub_send("item", item="Life Saver")
        price_message = await self.bot.wait_for("price")
        return await self.get_price_from_description(price_message)

    async def get_price_from_description(self, message):
        for embed in message.embeds:
            description = embed.description
            price_match = re.search(r"for ⏣ ([\d,.]+)", description)
            if price_match:
                price = price_match.group(1).replace(",", "")
                return int(price)
        return None

    async def get_total_amount(self):
        wallet_amount = await self.get_wallet_amount()
        bank_amount = await self.get_bank_amount()
        return wallet_amount + bank_amount

    async def get_wallet_amount(self):
        await self.bot.send("balance", channel)
        amount_message = await self.bot.wait_for("balance")
        amount_description = amount_message.embeds[0].description
        wallet_amount_match = re.search(r"Pocket\s*\n\s*⏣\s*([\d,.]+)", amount_description)
        if wallet_amount_match:
            wallet_amount = int(wallet_amount_match.group(1).replace(",", ""))
            return wallet_amount
        return 0

    async def get_bank_amount(self):
        await self.bot.send("balance", channel)
        amount_message = await self.bot.wait_for("balance")
        amount_description = amount_message.embeds[0].description
        bank_amount_match = re.search(r"Bank\s*\n\s*⏣\s*([\d,.]+)", amount_description)
        if bank_amount_match:
            bank_amount = int(bank_amount_match.group(1).replace(",", ""))
            return bank_amount
        return 0

def setup(bot):
    bot.add_cog(Autobuy(bot))
