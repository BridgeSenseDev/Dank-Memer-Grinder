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

        embed = message.embeds[0].to_dict()
        for pet in message.components[0].children[0].options:
            await message.components[0].children[0].choose(pet)
            await asyncio.sleep(1)
            for count, i in enumerate(embed["fields"]):
                percentage = int(
                    re.search(
                        "\((.*?)\)",
                        i["value"],
                    ).group(
                        1
                    )[:-1]
                )
                while percentage <= 90:
                    await self.bot.click(message, 1, count)
                    if count == 2:
                        break
                    await asyncio.sleep(0.5)
                    embed = message.embeds[0].to_dict()
                    percentage = int(
                        re.search(
                            "\((.*?)\)",
                            embed["fields"][count]["value"],
                        ).group(
                            1
                        )[:-1]
                    )


async def setup(bot):
    await bot.add_cog(Pets(bot))
