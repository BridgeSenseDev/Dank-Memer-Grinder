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


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chance = config_dict["trivia_correct_chance"]

    async def cog_load(self):
        self.dig.start()
        self.fish.start()
        self.hunt.start()
        self.beg.start()
        self.dep_all.start()
        self.work.start()
        self.daily.start()

    @tasks.loop(seconds=52)
    async def dig(self):
        if config_dict["commands"]["dig"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371078832204]):
                await cmd()
                break

    @tasks.loop(seconds=52)
    async def fish(self):
        if config_dict["commands"]["fish"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371078832206]):
                await cmd()
                break

    @tasks.loop(seconds=52)
    async def hunt(self):
        if config_dict["commands"]["hunt"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371171102760]):
                await cmd()
                break

    @tasks.loop(minutes=1)
    async def beg(self):
        if config_dict["commands"]["beg"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371041095699]):
                await cmd()
                break

    @tasks.loop(minutes=5)
    async def dep_all(self):
        if config_dict["commands"]["dep_all"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 300))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560370911072256]):
                await cmd(amount="max")
                break

    @tasks.loop(minutes=61)
    async def work(self):
        if config_dict["commands"]["work"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 780))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371267579942]):
                await cmd.shift()
                break

    @tasks.loop(hours=24)
    async def daily(self):
        if config_dict["commands"]["daily"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(500, 1000))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560370864930856]):
                await cmd.shift()
                break


async def setup(bot):
    await bot.add_cog(Commands(bot))
