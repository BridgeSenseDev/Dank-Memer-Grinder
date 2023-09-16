import json
import random
import time

from discord.ext import commands


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json", "r") as config_file:
            config_dict = json.load(config_file)
        search_config = config_dict[self.bot.account_id]["commands"]["search"]
        if "priority" not in search_config:
            search_config["priority"] = self.bot.config_example["commands"]["search"][
                "priority"
            ]
            search_config["second_priority"] = self.bot.config_example["commands"][
                "search"
            ]["second_priority"]
            search_config["avoid"] = self.bot.config_example["commands"]["search"][
                "avoid"
            ]
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

        self.priority = search_config["priority"]
        self.second_priority = search_config["second_priority"]
        self.avoid = search_config["avoid"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "search"):
            return

        children = message.components[0].children
        random.shuffle(children)
        for count, button in enumerate(children):
            if button.label.lower() in self.priority:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["search"] = time.time()
                return
        for count, button in enumerate(children):
            if button.label.lower() in self.second_priority:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["search"] = time.time()
                return
        for count, button in enumerate(children):
            if button.label.lower() not in self.avoid:
                await self.bot.click(message, 0, count)
                self.bot.last_ran["search"] = time.time()
                return


async def setup(bot):
    await bot.add_cog(Search(bot))
