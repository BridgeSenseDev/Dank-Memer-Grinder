import json
import os
import random
import re
import sys

import discord
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
            try:
                if (
                    "You have an unread alert!" in embed["title"]
                    and f"<@{self.bot.user.id}>" in message.content
                    and self.bot.config_dict["alerts"]
                ):
                    await self.bot.send("alert")
            except KeyError:
                pass

    @tasks.loop(seconds=15)
    async def presence(self):
        if not self.bot.state:
            return
        if (
            self.bot.config_dict["offline"]
            and self.bot.status != discord.Status.invisible
        ):
            await self.bot.change_presence(
                status=discord.Status.invisible, activity=self.bot.activity
            )
        elif (
            not self.bot.config_dict["offline"]
            and self.bot.status == discord.Status.invisible
        ):
            await self.bot.change_presence(
                status=discord.Status.online, activity=self.bot.activity
            )

    @presence.before_loop
    async def before_presence(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Others(bot))
