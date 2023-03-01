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
        if message.channel.id != self.bot.channel_id or self.bot.state is False:
            return
        for embed in message.embeds:
            embed = embed.to_dict()
            try:
                if (
                    "You have an unread alert!" in embed["title"]
                    and self.bot.config_dict["alerts"]
                ):
                    await self.bot.send("alert")
            except KeyError:
                pass

    @tasks.loop(seconds=30)
    async def presence(self):
        if self.bot.state is False:
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
