import asyncio
import json
import random

from discord.ext import commands


class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json", "r") as config_file:
            config_dict = json.load(config_file)
        stream_config = self.bot.config_dict["commands"]["stream"]
        if "order" not in stream_config:
            stream_config["order"] = self.bot.config_example["commands"]["stream"][
                "order"
            ]
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        self.order = stream_config["order"]
        self.click_counter = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "stream"):
            return

        embed = message.embeds[0].to_dict()

        # Go live
        try:
            if embed["fields"][1]["name"] == "Last Live":
                await self.bot.click(message, 0, 0)
                await asyncio.sleep(0.7)
                await self.bot.select(message, 0, 0, random.randint(0, 24))
                await asyncio.sleep(0.7)
                await self.bot.click(message, 1, 0)
        except (KeyError, IndexError):
            pass

        # Read chat
        try:
            if embed["fields"][1]["name"] == "Live Since":
                click_value = self.order[self.click_counter % len(self.order)]
                await self.bot.click(message, 0, click_value)
                print(click_value)
                self.click_counter += 1
        except (KeyError, IndexError):
            pass


async def setup(bot):
    await bot.add_cog(Stream(bot))
