import asyncio
import json
import random
import threading

from discord.ext import commands, tasks


def update():
    global commands_dict
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
    with open("commands.json", "r") as commands_file:
        commands_dict = json.load(commands_file)


update()

with open("trivia.json") as file:
    trivia_dict = json.load(file)


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

    @tasks.loop(seconds=52)
    async def dig(self):
        if commands_dict["dig"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371078832204]):
                await cmd()
                break

    @tasks.loop(seconds=52)
    async def fish(self):
        if commands_dict["fish"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371078832206]):
                await cmd()
                break

    @tasks.loop(seconds=52)
    async def hunt(self):
        if commands_dict["hunt"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371171102760]):
                await cmd()
                break

    @tasks.loop(minutes=1)
    async def beg(self):
        if commands_dict["beg"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 3))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371041095699]):
                await cmd()
                break

    @tasks.loop(minutes=5)
    async def dep_all(self):
        if commands_dict["dep_all"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 300))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560370911072256]):
                await cmd(amount="max")
                break

    @tasks.loop(minutes=61)
    async def work(self):
        if commands_dict["work"] is True and commands_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 780))
            async for cmd in self.bot.channel.slash_commands(command_ids=[1011560371267579942]):
                await cmd.shift()
                break


async def setup(bot):
    await bot.add_cog(Commands(bot))
