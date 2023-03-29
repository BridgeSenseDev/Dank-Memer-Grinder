import re

from discord.ext import commands


class Autobuy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild or not self.bot.state:
            return
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
                        await self.bot.sub_send(
                            "shop",
                            "buy",
                            channel,
                            item="Life Saver",
                            quantity=str(required - remaining),
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

        for embed in message.embeds:
            embed = embed.to_dict()
            # Shovel
            try:
                if (
                    "You don't have a shovel, you need to go buy one."
                    in embed["description"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.bot.sub_send("shop", "buy", item="Shovel", quantity="1")
            except KeyError:
                pass

            # Fishing pole
            try:
                if (
                    "You don't have a fishing pole, you need to go buy one"
                    in embed["description"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.bot.sub_send(
                        "shop", "buy", item="Fishing Pole", quantity="1"
                    )
            except KeyError:
                pass

            # Hunting rifle
            try:
                if (
                    "You don't have a hunting rifle, you need to go buy one."
                    in embed["description"]
                ):
                    await self.bot.send("withdraw", amount="35k")
                    await self.bot.sub_send(
                        "shop", "buy", item="Hunting Rifle", quantity="1"
                    )
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Autobuy(bot))
