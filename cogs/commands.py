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
        if self.bot.state is False:
            await asyncio.sleep(1)
            return
        for command in self.bot.commands_dict:
            if (
                time.time() - self.bot.last_ran[command]
                < self.bot.config_dict["commands"][command]["delay"]
                or self.bot.config_dict["commands"][command]["state"] is False
            ):
                await asyncio.sleep(0.5)
                continue
            self.bot.last_ran[command] = time.time()
            if command == "dep_all":
                await self.bot.send(self.bot.commands_dict[command], amount="max")
                await asyncio.sleep(random.randint(2, 4))
                continue
            elif command == "work":
                await self.bot.sub_send(self.bot.commands_dict[command], "shift")
                await asyncio.sleep(random.randint(2, 4))
                continue
            elif command == "pet":
                await self.bot.sub_send(self.bot.commands_dict[command], "care")
                await asyncio.sleep(random.randint(2, 4))
                continue
            await self.bot.send(self.bot.commands_dict[command])
            await asyncio.sleep(random.randint(2, 4))
            return


async def setup(bot):
    await bot.add_cog(Commands(bot))
