import contextlib
import json

import discord
from PyQt5.QtGui import QColor
from discord.ext import commands, tasks


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return
        for embed in message.embeds:
            embed = embed.to_dict()
            with contextlib.suppress(KeyError):
                if (
                    "You have an unread alert!" in embed["title"]
                    and f"<@{self.bot.user.id}>" in message.content
                    and self.bot.config_dict["alerts"]
                ):
                    await self.bot.send("alert")
            with contextlib.suppress(KeyError):
                if (
                    "unable to interact with this due to an ongoing command"
                    in embed["description"]
                ):
                    self.bot.last_ran = {
                        k: v + 30 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
            with contextlib.suppress(KeyError):
                if "maintenance" in embed["title"].lower():
                    with open("config.json", "r+") as config_file:
                        config_dict = json.load(config_file)
                        for account_id in (str(i) for i in range(1, len(config_dict))):
                            config_dict[account_id]["state"] = False
                            self.bot.window.output.emit(
                                [
                                    f"output_text_{account_id}",
                                    (
                                        "All bots have been disabled because of a dank"
                                        " memer maintenance\nPlease check if the update"
                                        " is safe before continuing to grind"
                                    ),
                                    QColor(216, 60, 62),
                                ]
                            )
                        config_file.seek(0)
                        json.dump(config_dict, config_file, indent=4)
                        config_file.truncate()

                    self.bot.window.ui.toggle.setStyleSheet(
                        "background-color : #d83c3e"
                    )
                    account = self.bot.window.ui.accounts.currentText()
                    self.bot.window.ui.toggle.setText(
                        " ".join(account.split()[:-1] + ["Disabled"])
                    )

    @tasks.loop(seconds=15)
    async def presence(self):
        if not self.bot.state:
            return
        if (
            self.bot.config_dict["offline"]
            and self.bot.status != discord.Status.invisible
        ):
            await self.bot.change_presence(status=discord.Status.invisible)
        elif (
            not self.bot.config_dict["offline"]
            and self.bot.status == discord.Status.invisible
        ):
            await self.bot.change_presence(status=discord.Status.online)

    @presence.before_loop
    async def before_presence(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Others(bot))
