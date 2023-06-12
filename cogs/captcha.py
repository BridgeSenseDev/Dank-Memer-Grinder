import json

from PyQt5.QtGui import QColor
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
            if "we're under maintenance!" in embed["title"].lower():
                with open("config.json", "r+") as config_file:
                    config_dict = json.load(config_file)
                    for account_id in (str(i) for i in range(1, len(config_dict))):
                        config_dict[account_id]["state"] = False
                        self.bot.window.output.emit(
                            [
                                f"output_text_{account_id}",
                                (
                                    "All bots have been disabled because of a dank"
                                    " memer maintenance\nPlease check if the update is"
                                    " safe before continuing to grind"
                                ),
                                QColor(216, 60, 62),
                            ]
                        )
                    config_file.seek(0)
                    json.dump(config_dict, config_file, indent=4)
                    config_file.truncate()

                self.bot.window.ui.toggle.setStyleSheet("background-color : #d83c3e")
                account = self.bot.window.ui.accounts.currentText()
                self.bot.window.ui.toggle.setText(
                    " ".join(account.split()[:-1] + ["Disabled"])
                )
                return

            if "captcha" not in embed["title"].lower():
                return

            # Matching image captcha
            if (
                "**click the button with matching image.**\nfailing the captcha might"
                " result in a temporary ban."
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Matching Image Captcha",
                    "red",
                )
                captcha_url = embed["image"]["url"]
                for count, button in enumerate(message.components[0].children):
                    if button.emoji.url in captcha_url:
                        await self.bot.click(message, 0, count)
                        self.bot.log(
                            f"Matching Image Captcha Solved",
                            "green",
                        )
                        return

            # Pepe captcha
            if (
                "**click all buttons with a pepe (green frog) in it.**\nfailing the"
                " captcha might result in a temporary ban."
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
                            await self.bot.click(message, row, column)
                            continue
        except KeyError:
            pass


async def setup(bot):
    await bot.add_cog(Captcha(bot))
