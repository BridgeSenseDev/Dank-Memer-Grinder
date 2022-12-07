import asyncio
import random
import time

from discord.ext import commands, tasks


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.commands.start()

    @tasks.loop(seconds=0.05)
    async def commands(self):
        if self.bot.config_dict[self.bot.account_id]["state"] is False:
            await asyncio.sleep(1)
            return
        for command in self.bot.commands_list:
            # Handled in cogs
            if command == "bj":
                continue
            if (
                time.time() - self.bot.last_ran[command]
                < self.bot.commands_delay[command]
                or self.bot.config_dict[self.bot.account_id]["commands"][command]
                is False
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
            return


async def setup(bot):
    await bot.add_cog(Commands(bot))
