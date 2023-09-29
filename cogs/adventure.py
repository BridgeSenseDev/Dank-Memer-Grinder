import asyncio
import contextlib
import json

from discord.ext import commands


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

        with contextlib.suppress(KeyError):
            embed = after.embeds[0].to_dict()
            if embed["author"]["name"] == "Adventure Summary":
                self.bot.pause_commands = False

        with contextlib.suppress(KeyError):
            embed = after.embeds[0].to_dict()
            if "choose items you want to" in embed["title"]:
                for count, component in enumerate(after.components):
                    if component.children[0].label == "Start":
                        await self.bot.click(after, count, 0)
                        return
                return

        with contextlib.suppress(KeyError):
            embed = after.embeds[0].to_dict()
            if "You can start another adventure at" in embed["description"]:
                return

            for i in range(2):
                with contextlib.suppress(AttributeError):
                    button = after.components[i].children[1]
                    if not button.disabled and button.emoji.id == 1067941108568567818:
                        await self.bot.click(after, i, 1)
                        return

            if "Catch one of em!" in embed["description"]:
                await self.bot.click(after, 0, 2)
                await self.bot.click(after, 1, 1)
                return

            question = embed["description"].split("\n")[0]
            for q, answer in self.bot.global_config_dict["adventure"][
                self.adventure
            ].items():
                if q.lower() in question.lower():
                    for count, button in enumerate(after.components[0].children):
                        if button.label.lower() == answer.lower():
                            await self.bot.click(after, 0, count)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.bot.is_valid_command(message, "adventure"):
            return

        with contextlib.suppress(KeyError):
            embed = message.embeds[0].to_dict()
            if embed["author"]["name"] == "Choose an Adventure":
                for count, i in enumerate(message.components[0].children[0].options):
                    if i.value == self.adventure:
                        await self.bot.select(message, 0, 0, count)
                        if not message.components[1].children[0].disabled:
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, 1, 0)
                        else:
                            self.bot.pause_commands = False


async def setup(bot):
    await bot.add_cog(Adventure(bot))
