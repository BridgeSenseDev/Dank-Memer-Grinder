import json
import random
import time

from discord.ext import commands


class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json", "r") as config_file:
            config_dict = json.load(config_file)
        crime_config = config_dict[self.bot.account_id]["commands"]["crime"]
        if "priority" not in crime_config:
            crime_config["priority"] = self.bot.config_example["commands"]["crime"][
                "priority"
            ]
            crime_config["second_priority"] = self.bot.config_example["commands"][
                "crime"
            ]["second_priority"]
            crime_config["avoid"] = self.bot.config_example["commands"]["crime"][
                "avoid"
            ]
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

        self.priority = crime_config["priority"]
        self.second_priority = crime_config["second_priority"]
        self.avoid = crime_config["avoid"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "crime"):
            return

        children = message.components[0].children
        random.shuffle(children)
        for count, button in enumerate(children):
            if button.label.lower() in self.priority:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["crime"] = time.time()
                return
        for count, button in enumerate(children):
            if button.label.lower() in self.second_priority:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["crime"] = time.time()
                return
        for count, button in enumerate(children):
            if button.label.lower() not in self.avoid:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["crime"] = time.time()
                return


async def setup(bot):
    await bot.add_cog(Crime(bot))
