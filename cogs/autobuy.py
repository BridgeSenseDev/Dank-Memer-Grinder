import re
from discord.ext import commands

class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and self.bot.state:
            channel = await message.author.create_dm()

            for embed in message.embeds:
                embed = embed.to_dict()

                # Buy lifesavers
                try:
                    if (
                        embed["title"] == "Your lifesaver protected you!"
                        and self.bot.config_dict.get("autobuy", {}).get("lifesavers", {}).get("state")
                    ):
                        remaining = int(re.search(r"have (.*?)x Life Saver", message.components[0].children[0].label).group(1))
                        required = int(self.bot.config_dict.get("autobuy", {}).get("lifesavers", {}).get("amount"))
                        if remaining < required:
                            price = await self.get_price_from_shop("Life Saver")

                            if price is None:
                                price = await self.get_failsafe_amount("Life Saver")
                                self.bot.log("Failed to retrieve the price. Using failsafe price.", "red")

                            total_amount = await self.get_total_amount()
                            if price <= total_amount:
                                wallet_amount = total_amount
                                if price > wallet_amount:
                                    withdrawal_amount = price - wallet_amount
                                    await self.bot.send("withdraw", channel, str(withdrawal_amount))
                                await self.bot.sub_send("shop", "buy", channel, item="Life Saver", quantity=str(required))
                                self.bot.log(f"Bought {required} Lifesavers.", "yellow")
                            else:
                                self.bot.log("Insufficient funds to buy Lifesavers.", "red")
                except KeyError:
                    pass

                # Confirm purchase
                try:
                    if embed["title"] == "Pending Confirmation" and self.bot.config_dict["autobuy"]["lifesavers"]["state"]:
                        await self.bot.click(message, 0, 1)
                except KeyError:
                    pass

                # Buy missing items
                try:
                    items = {
                        "Shovel": self.bot.config_dict["autobuy"]["shovel"],
                        "Fishing Pole": self.bot.config_dict["autobuy"]["fishing_pole"],
                        "Hunting Rifle": self.bot.config_dict["autobuy"]["rifle"]
                    }
                    for item, config_enabled in items.items():
                        if f"You don't have a {item.lower()}, you need to go buy one." in embed["description"] and config_enabled:
                            price = await self.get_price_from_shop(item)
                            if price is None:
                                price = await self.get_failsafe_amount(item)
                                self.bot.log(f"Failed to retrieve the price for {item}. Using failsafe price.", "red")
                            if price <= total_amount:
                                await self.bot.send("withdraw", channel, str(price))
                                await self.bot.sub_send("shop", "buy", item=item, quantity="1")
                                self.bot.log(f"Bought {item}.", "yellow")
                            else:
                                self.bot.log(f"Insufficient funds to buy {item}.", "red")
                except KeyError:
                    pass

        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

    async def get_price_from_shop(self, item):
        await self.bot.sub_send("item", item=item)
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
        await self.bot.send("balance")
        amount_message = await self.bot.wait_for("balance")
        amount_description = amount_message.embeds[0].description
        wallet_amount_match = re.search(r"Pocket\s*\n\s*⏣\s*([\d,]+)", amount_description)
        bank_amount_match = re.search(r"Bank\s*\n\s*⏣\s*([\d,]+)", amount_description)

        if wallet_amount_match and bank_amount_match:
            wallet_amount = int(wallet_amount_match.group(1).replace(",", ""))
            bank_amount = int(bank_amount_match.group(1).replace(",", ""))
            return wallet_amount + bank_amount
        return 0

    async def get_failsafe_amount(self, item):
        failsafe_amounts = {
            "Shovel": 35000,
            "Fishing Pole": 35000,
            "Hunting Rifle": 35000,
            "Life Saver": 250000,
        }
        return failsafe_amounts.get(item, 0)

async def setup(bot):
    bot.add_cog(Autobuy(bot))
