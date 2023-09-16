import asyncio
import contextlib
import re
import time

import discord.errors
from discord.ext import commands

items = {
    "shovel": {
        "name": "Shovel",
        "internal_name": "shovel",
        "message": "You don't have a shovel, you need to go buy one",
        "cost": "45k",
    },
    "pole": {
        "name": "Fishing Pole",
        "internal_name": "fishing",
        "message": "You don't have a fishing pole, you need to go buy one",
        "cost": "35k",
    },
    "rifle": {
        "name": "Hunting Rifle",
        "internal_name": "rifle",
        "message": "You don't have a hunting rifle, you need to go buy one",
        "cost": "45k",
    },
}


class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_message = None

    async def shop_buy(self, item, count=1):
        await self.bot.sub_send("shop", "view")

        def check(msg):
            try:
                return msg.embeds[0].to_dict()["title"] == "Dank Memer Shop"
            except (KeyError, IndexError):
                return False

        message = await self.bot.wait_for("message", check=check)
        if message.components[3].children[1].emoji.id == 1105833876032606350:
            await self.bot.click(message, 3, 1)
            await asyncio.sleep(0.5)

        embed = message.embeds[0].to_dict()
        pages = int(re.search(r"Page \d+ of (\d+)", embed["footer"]["text"]).group(1))

        for i in range(pages):
            for row in range(1, 3):
                for col, button in enumerate(message.components[row].children):
                    if item in button.label.lower():
                        if message.components[row].children[col].disabled:
                            return False
                        await self.bot.click(message, row, col)

                        modal = await self.bot.wait_for("modal")
                        modal.components[0].children[0].answer(str(count))

                        try:
                            await modal.submit()
                        except (
                            discord.errors.HTTPException,
                            discord.errors.InvalidData,
                        ):
                            pass
                        return

            await self.bot.click(message, 3, 2)
            await asyncio.sleep(0.3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.state or (
            message.channel.id != self.bot.channel_id and message.guild
        ):
            return

        for embed in message.embeds:
            embed = embed.to_dict()

            # Successful Purchase
            with contextlib.suppress(KeyError):
                if embed["title"] == "Successful Purchase":
                    for item, details in items.items():
                        if item in embed["description"].lower():
                            items_bought = int(
                                re.search(r"(\d+)x", embed["description"]).group(1)
                            )
                            amount_paid = re.search(
                                r"You paid:\*\*\n- ⏣ (\d{1,3}(,\d{3})*(\.\d+)?)",
                                embed["description"],
                            ).group(1)
                            self.bot.log(
                                f"Bought {items_bought}x {details['name']} for "
                                f"⏣ {amount_paid}",
                                "green",
                            )
                            return
                elif "don't have enough coins in your wallet" in embed["description"]:
                    self.bot.log("Not enough coins in wallet to buy that much", "red")
                    return

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
                        self.bot.pause_commands = True
                        self.bot.pause_commands_timestamp = time.time()

                        await self.bot.send(
                            "withdraw",
                            amount=str((required - remaining) * 250000),
                        )

                        await asyncio.sleep(0.3)
                        await self.shop_buy("saver", required - remaining)

                        self.bot.pause_commands = False
                        return

            # Confirm purchase
            with contextlib.suppress(KeyError):
                if (
                    embed["title"] == "Pending Confirmation"
                    and self.bot.config_dict["autobuy"]["lifesavers"]["state"]
                ):
                    await self.bot.click(message, 0, 1)

        for embed in message.embeds:
            embed = embed.to_dict()

            for item, details in items.items():
                with contextlib.suppress(KeyError):
                    if (
                        details["message"] in embed["description"]
                        and self.bot.config_dict["autobuy"][details["internal_name"]]
                    ):
                        self.bot.pause_commands = True
                        self.bot.pause_commands_timestamp = time.time()

                        await asyncio.sleep(0.3)
                        await self.bot.send("withdraw", amount=details["cost"])
                        await asyncio.sleep(0.3)
                        await self.shop_buy(item, 1)

                        self.bot.pause_commands = False

                        def check(msg):
                            try:
                                return (
                                    msg.embeds[0].to_dict()["title"]
                                    == "Pending Confirmation"
                                )
                            except (KeyError, IndexError):
                                return False

                        message = await self.bot.wait_for("message", check=check)
                        await self.bot.click(message, 0, 0)


async def setup(bot):
    await bot.add_cog(Autobuy(bot))
