import asyncio
import contextlib
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

        self.bot.pause = True

        with contextlib.suppress(AttributeError):
            await self.bot.send(
                "withdraw",
                amount=f"{10 * len(message.components[0].children[0].options)}k",
            )

            for pet in message.components[0].children[0].options:
                await message.components[0].children[0].choose(pet)
                await asyncio.sleep(0.5)
                if message.components[1].children[0].disabled:
                    continue
                embed = message.embeds[0].to_dict()
                for count, i in enumerate(embed["fields"]):
                    percentage = 100
                    if match := re.search(r"\((\d{1,3})%\)", i["value"]):
                        percentage = int(match[1])
                    while percentage < 90:
                        await self.bot.click(message, 1, count)
                        if count == 2:
                            await asyncio.sleep(10)
                            await self.bot.click(message, 2, 1)
                            await self.bot.click(message, 2, 2)
                            break
                        await asyncio.sleep(0.5)
                        embed = message.embeds[0].to_dict()
                        percentage = (
                            int(match.group(1))
                            if (
                                match := re.search(
                                    r"\((\d{1,3})%\)",
                                    embed["fields"][count]["value"],
                                )
                            )
                            else 100
                        )
        self.bot.pause = False


async def setup(bot):
    await bot.add_cog(Pets(bot))
