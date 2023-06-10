import asyncio
import json

from discord.ext import commands, tasks


class Adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_ran = {}
        with open("config.json", "r") as config_file:
            config_dict = json.load(config_file)
        adventure_config = config_dict[self.bot.account_id]["commands"]["adventure"]
        if "adventure" not in adventure_config:
            adventure_config["adventure"] = self.bot.config_example["commands"][
                "adventure"
            ]["adventure"]
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        self.adventure = adventure_config["adventure"]
        adventure_box = getattr(
            self.bot.window.ui, f"adventure_box_{self.bot.account_id}"
        )
        adventure_box.setCurrentIndex(adventure_box.findText(self.adventure))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not await self.bot.is_valid_command(after, "adventure"):
            return

        try:
            embed = after.embeds[0].to_dict()
            if embed["author"]["name"] == "Adventure Summary":
                self.bot.last_ran = {
                    k: v - 100 if v != float("inf") else 0
                    for k, v in self.bot.last_ran.items()
                }
                return
        except KeyError:
            pass

        try:
            embed = after.embeds[0].to_dict()
            if "choose items you want to take with you" in embed["title"]:
                await asyncio.sleep(0.5)
                await self.bot.click(after, 2, 0)
                return
        except KeyError:
            pass

        try:
            embed = after.embeds[0].to_dict()
            if "You can start another adventure at" in embed["description"]:
                return

            for i in range(2):
                try:
                    button = after.components[i].children[1]
                    if not button.disabled and button.emoji.id == 1067941108568567818:
                        await asyncio.sleep(0.5)
                        await self.bot.click(after, i, 1)
                        return
                except AttributeError:
                    pass

            if "Catch one of em!" in embed["description"]:
                await asyncio.sleep(0.5)
                await self.bot.click(after, 0, 2)
                await asyncio.sleep(0.5)
                await self.bot.click(after, 1, 1)
                return

            question = embed["description"].split("\n")[0]
            for q, answer in self.bot.global_config_dict[self.adventure].items():
                if q.lower() in question.lower():
                    for count, button in enumerate(after.components[0].children):
                        if button.label.lower() == answer.lower():
                            await asyncio.sleep(0.5)
                            await self.bot.click(after, 0, count)
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "adventure"):
            return

        try:
            embed = message.embeds[0].to_dict()
            if embed["author"]["name"] == "Choose an Adventure":
                for count, i in enumerate(message.components[0].children[0].options):
                    if i.value == self.adventure:
                        await asyncio.sleep(0.5)
                        await self.bot.select(message, 0, 0, count)
                        await asyncio.sleep(0.5)
                        if not message.components[1].children[0].disabled:
                            await self.bot.click(message, 1, 0)
                            self.bot.last_ran = {
                                k: v + 100 if v != 0 else float("inf")
                                for k, v in self.bot.last_ran.items()
                            }

        except KeyError:
            pass


async def setup(bot):
    await bot.add_cog(Adventure(bot))
