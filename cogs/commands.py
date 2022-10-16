import asyncio
import json
import random
import threading
import time

from discord.ext import commands


def update():
    global config_dict
    threading.Timer(5, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chance = config_dict[self.bot.account_id]["trivia_correct_chance"]

    async def cog_load(self):
        self.bot.channel_id = config_dict[self.bot.account_id]["channel_id"]
        self.bot.channel = self.bot.get_channel(self.bot.channel_id)
        while True:
            if config_dict[self.bot.account_id]["state"] is False:
                await asyncio.sleep(1)
                continue
            for command in self.bot.commands_list:
                # Handled in cogs
                if command == "bj":
                    continue
                if (
                    time.time() - self.bot.last_ran[command]
                    < self.bot.commands_delay[command]
                    or config_dict[self.bot.account_id]["commands"][command] is False
                ):
                    await asyncio.sleep(0.5)
                    continue
                if command == "dep_all":
                    await self.bot.send(self.bot.commands_list[command], amount="max")
                    self.bot.last_ran[command] = time.time()
                    await asyncio.sleep(random.randint(2, 4))
                    continue
                if command == "work":
                    await self.bot.sub_send(self.bot.commands_list[command], "shift")
                    self.bot.last_ran[command] = time.time()
                    await asyncio.sleep(random.randint(2, 4))
                    continue
                await self.bot.send(self.bot.commands_list[command])
                self.bot.last_ran[command] = time.time()
                await asyncio.sleep(random.randint(2, 4))
                continue


async def setup(bot):
    await bot.add_cog(Commands(bot))
