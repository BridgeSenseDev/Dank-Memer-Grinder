import asyncio
import random
import threading
import json
import re
from discord.ext import commands, tasks

Games = {
    "Apex Legends": 0,
    "COD Warzone": 1,
    "CS GO": 2,
    "Dead by Daylight": 3,
    "Destiny 2": 4,
    "Dota 2": 5,
    "Elden Ring": 6,
    "Escape from Tarkov": 7,
    "FIFA 22": 8,
    "Fortnite": 9,
    "Grand Theft Auto V": 10,
    "Hearthstone": 11,
    "Just Chatting": 12,
    "League of Legends": 13,
    "Lost Ark": 14,
    "Minecraft": 15,
    "Music": 16,
    "PUBG Battlegrounds": 17,
    "Rainbow Six Siege": 18,
    "Rocket League": 19,
    "Rust": 20,
    "Teamfight Tactics": 21,
    "Valorant": 22,
    "World of Tanks": 23,
    "World of Warcraft": 24,
    "World Of Warcraft": 24,
}


def update():
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.pls_stream.start()

    @tasks.loop(minutes=11)
    async def pls_stream(self):
        if config_dict["commands"]["stream"] is True and config_dict["state"] is True:
            await asyncio.sleep(random.randint(0, 180))
            async for cmd in self.bot.channel.slash_commands(
                command_ids=[1011560371267579938]
            ):
                await cmd()
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or config_dict["state"] is False
            or config_dict["commands"]["stream"] is False
        ):
            return

        for embed in message.embeds:
            # Get trending game
            try:
                if embed.to_dict()["title"] == "Trending Game":
                    global game
                    game = Games[
                        (
                            re.search(
                                "\*\*(.*?)\*\*", embed.to_dict()["description"]
                            ).group(1)
                        ).title()
                    ]
            except:
                pass

            # Go live
            try:
                if embed.to_dict()["fields"][1]["name"] == "Last Live":
                    await message.components[0].children[0].click()

                    # Get trending game
                    async for cmd in self.bot.channel.slash_commands(
                        command_ids=[967369106301026344]
                    ):
                        await cmd()
                        break
                    await asyncio.sleep(4)

                    # Select trending game
                    await message.components[0].children[0].choose(
                        message.components[0].children[0].options[game]
                    )
                    await asyncio.sleep(0.7)
                    await message.components[1].children[0].click()
                    await asyncio.sleep(0.7)
                    await message.components[0].children[1].click()
            except:
                pass

            # Read chat
            try:
                if embed.to_dict()["fields"][1]["name"] == "Live Since":
                    await message.components[0].children[1].click()
            except:
                pass


async def setup(bot):
    await bot.add_cog(Stream(bot))
