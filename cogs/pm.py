import asyncio
import json
import random
import threading

from discord.ext import commands, tasks


def update():
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class Pm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.pm.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or config_dict["commands"]["pm"] is False
            or config_dict["state"] is False
        ):
            return

        for embed in message.embeds:
            try:
                if "meme posting session" in embed.to_dict()["author"]["name"]:
                    await message.components[0].children[random.randint(0, 4)].click()
            except KeyError:
                pass

    @tasks.loop(minutes=1)
    async def pm(self):
        if config_dict["commands"]["pm"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(
                command_ids=[1011560370911072263]
            ):
                await cmd()
                return


async def setup(bot):
    await bot.add_cog(Pm(bot))
