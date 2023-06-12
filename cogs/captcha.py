import asyncio

from discord.ext import commands


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

        try:
            embed = message.embeds[0].to_dict()
            if "captcha" not in embed["title"].lower():
                return

            # Matching image captcha
            if (
                "**click the button with matching image.**\nfailing the captcha might result in a temporary ban."
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Matching Image Captcha",
                    "red",
                )
                captcha_url = embed["image"]["url"]
                for count, button in enumerate(message.components[0].children):
                    if button.emoji.url in captcha_url:
                        await asyncio.sleep(0.5)
                        await self.bot.click(message, 0, count)
                        self.bot.log(
                            f"Matching Image Captcha Solved",
                            "green",
                        )
                        return

            # Pepe captcha
            if (
                "**click all buttons with a pepe (green frog) in it.**\nfailing the captcha might result in a temporary ban."
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Pepe Captcha",
                    "red",
                )
                for row, i in enumerate(message.components):
                    for column, button in enumerate(i.children):
                        if not button.emoji:
                            await self.bot.click(message, row, column)
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, row, column)
                            self.bot.log(
                                f"Pepe Captcha Solved",
                                "red",
                            )
                            return
                        if button.emoji.id in [
                            819014822867894304,
                            796765883120353280,
                            860602697942040596,
                            860602923665588284,
                            860603013063507998,
                            936007340736536626,
                            933194488241864704,
                            680105017532743700,
                        ]:
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, row, column)
                            continue

            # Reverse images captcha
            if "pick any of the three wrong images" in embed["description"].lower():
                self.bot.log(
                    f"Wrong Images Captcha",
                    "red",
                )
                captcha_url = embed["image"]["url"]
                for count, button in enumerate(message.components[0].children):
                    if button.emoji.url not in captcha_url:
                        await asyncio.sleep(0.5)
                        await self.bot.click(message, 0, count)
                self.bot.log(
                    f"Wrong Images Captcha Solved",
                    "green",
                )
                return

            # Reverse pepe captcha
            if (
                "click all buttons without a pepe in them!"
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Reverse Pepe Captcha",
                    "red",
                )
                for row, i in enumerate(message.components):
                    for column, button in enumerate(i.children):
                        if not button.emoji:
                            await self.bot.click(message, row, column)
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, row, column)
                            self.bot.log(
                                f"Pepe Captcha Solved",
                                "red",
                            )
                            return
                        if button.emoji.id not in [
                            819014822867894304,
                            796765883120353280,
                            860602697942040596,
                            860602923665588284,
                            860603013063507998,
                            936007340736536626,
                            933194488241864704,
                            680105017532743700,
                        ]:
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, row, column)
                            continue
        except KeyError:
            pass


async def setup(bot):
    await bot.add_cog(Captcha(bot))
