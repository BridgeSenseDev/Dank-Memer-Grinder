import json
import re
import threading

from discord.ext import commands


def update():
    global config_dict
    threading.Timer(1, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.guild is None
            and message.author.id == 270904126974590976
            and config_dict[self.bot.account_id]["state"] is True
        ):
            for embed in message.embeds:
                # Buy lifesavers
                try:
                    if (
                        embed.to_dict()["title"] == "Your lifesaver protected you!"
                        and config_dict[self.bot.account_id]["autobuy"]["lifesavers"][
                            "state"
                        ]
                        is True
                    ):
                        remaining = int(
                            re.search(
                                "have (.*?)x Life Saver",
                                message.components[0].children[0].label,
                            ).group(1)
                        )
                        required = int(
                            config_dict[self.bot.account_id]["autobuy"]["lifesavers"][
                                "amount"
                            ]
                        )
                        if remaining < required:
                            channel = await message.author.create_dm()
                            await self.bot.send(
                                "withdraw", amount=str((required - remaining) * 85000)
                            )
                            async for cmd in channel.slash_commands(
                                query="buy", limit=None
                            ):
                                await cmd(
                                    item="Life Saver",
                                    quantity=str(required - remaining),
                                )
                                break
                            return
                except KeyError:
                    pass

                # Confirm purchase
                try:
                    if (
                        embed.to_dict()["title"] == "Pending Confirmation"
                        and config_dict[self.bot.account_id]["autobuy"]["lifesavers"][
                            "state"
                        ]
                        is True
                    ):
                        await self.bot.click(message, 0, 1)
                except KeyError:
                    pass

        if (
            message.channel.id != self.bot.channel_id
            or config_dict[self.bot.account_id]["state"] is False
        ):
            return

        for embed in message.embeds:
            # Shovel
            try:
                if (
                    "You don't have a shovel, you need to go buy one."
                    in embed.to_dict()["description"]
                ):
                    await self.bot.send("withdraw", amount="25k")
                    await self.bot.send("buy", item="Shovel", quantity="1")
            except KeyError:
                pass

            # Fishing pole
            try:
                if (
                    "You don't have a fishing pole, you need to go buy one"
                    in embed.to_dict()["description"]
                ):
                    await self.bot.send("withdraw", amount="25k")
                    await self.bot.send("buy", item="Fishing Pole", quantity="1")
            except KeyError:
                pass

            # Hunting rifle
            try:
                if (
                    "You don't have a hunting rifle, you need to go buy one."
                    in embed.to_dict()["description"]
                ):
                    await self.bot.send("withdraw", amount="25k")
                    await self.bot.send("buy", item="Hunting Rifle", quantity="1")
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Autobuy(bot))
