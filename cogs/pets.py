import asyncio
import re

from discord.ext import commands

priority = []
second_priority = []
avoid = []


class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "pet", "care"):
            return

        self.bot.last_ran = {
            k: v + 100 if v != 0 else float("inf") for k, v in self.bot.last_ran.items()
        }

        try:
            for pet in message.components[0].children[0].options:
                await self.bot.send("withdraw", amount="40k")
                await message.components[0].children[0].choose(pet)
                await asyncio.sleep(1)
                if message.components[1].children[0].disabled:
                    continue
                embed = message.embeds[0].to_dict()
                for count, i in enumerate(embed["fields"]):
                    percentage = 100
                    match = re.search(r"\((\d{1,3})%\)", i["value"])
                    if match:
                        percentage = int(match.group(1))
                    while percentage < 90:
                        await self.bot.click(message, 1, count)
                        if count == 2:
                            await asyncio.sleep(10)
                            await self.bot.click(message, 2, 1)
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, 2, 2)
                            break
                        await asyncio.sleep(0.5)
                        embed = message.embeds[0].to_dict()
                        match = re.search(
                            r"\((\d{1,3})%\)", embed["fields"][count]["value"]
                        )
                        if match:
                            percentage = int(match.group(1))
                        else:
                            percentage = 100
        except AttributeError:
            pass

        self.bot.last_ran = {
            k: v - 100 if v != float("inf") else 0 for k, v in self.bot.last_ran.items()
        }


async def setup(bot):
    await bot.add_cog(Pets(bot))
