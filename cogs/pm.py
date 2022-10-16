import json
import random
import threading

from discord.ext import commands


def update():
    global config_dict
    threading.Timer(5, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class Pm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or config_dict[self.bot.account_id]["commands"]["pm"] is False
            or config_dict[self.bot.account_id]["state"] is False
        ):
            return

        for embed in message.embeds:
            try:
                if "meme posting session" in embed.to_dict()["author"]["name"]:
                    await self.bot.click(message, 0, random.randint(0, 4))
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Pm(bot))
