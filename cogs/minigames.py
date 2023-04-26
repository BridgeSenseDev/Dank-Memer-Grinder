import asyncio
import re

from discord.ext import commands

moleman_loc = {
    "<a:MoleMan:1022972147175526441><:emptyspace:827651824739156030><:emptyspace:827651824739156030>": (
        0
    ),
    "<:emptyspace:827651824739156030><a:MoleMan:1022972147175526441><:emptyspace:827651824739156030>": (
        1
    ),
    "<:emptyspace:827651824739156030><:emptyspace:827651824739156030><a:MoleMan:1022972147175526441>": (
        2
    ),
}

worms_loc = {
    "<:emptyspace:827651824739156030><:Worm:864261394920898600><:Worm:864261394920898600>": (
        0
    ),
    "<:Worm:864261394920898600><:emptyspace:827651824739156030><:Worm:864261394920898600>": (
        1
    ),
    "<:Worm:864261394920898600><:Worm:864261394920898600><:emptyspace:827651824739156030>": (
        2
    ),
}


class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if (
            after.channel.id != self.bot.channel_id
            or not self.bot.state
            or (after.interaction and after.interaction.user != self.bot.user)
        ):
            return

        for embed in after.embeds:
            embed = embed.to_dict()
            # MoleMan
            try:
                if "Dodge the Worms!" in embed["description"]:
                    moleman = embed["description"].splitlines()[5]
                    for i in reversed(embed["description"].splitlines()):
                        if i not in worms_loc:
                            continue
                        match worms_loc[i]:
                            case 0:
                                if moleman_loc[moleman] == 1:
                                    await self.bot.click(after, 0, 0)
                                elif moleman_loc[moleman] == 2:
                                    await self.bot.click(after, 0, 0)
                                    await asyncio.sleep(0.2)
                                    await self.bot.click(after, 0, 0)
                                break
                            case 1:
                                if moleman_loc[moleman] == 0:
                                    await self.bot.click(after, 0, 1)
                                elif moleman_loc[moleman] == 2:
                                    await self.bot.click(after, 0, 0)
                                break
                            case 2:
                                if moleman_loc[moleman] == 0:
                                    await self.bot.click(after, 0, 1)
                                    await asyncio.sleep(0.2)
                                    await self.bot.click(after, 0, 1)
                                if moleman_loc[moleman] == 1:
                                    await self.bot.click(after, 0, 1)
                                break
                    return
            except KeyError:
                pass

            # Football
            try:
                if "Hit the ball!" in embed["description"]:
                    if ":levitate:" == embed["description"].splitlines()[2]:
                        await self.bot.click(after, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>:levitate:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 0)
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:levitate:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 1)
                    return
            except KeyError:
                pass

            # Basketball
            try:
                if "Dunk the ball!" in embed["description"]:
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:basketball:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>:basketball:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 1)
                    elif ":basketball:" == embed["description"].splitlines()[2]:
                        await self.bot.click(after, 0, 0)
                    return
            except KeyError:
                pass

            # Dragon
            try:
                if "Dodge the Fireball" in embed["description"]:
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 0)
                    elif (
                        "<:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(after, 0, 2)
                    return
            except KeyError:
                pass

            # Catch the fish
            try:
                if "Catch the fish!" in embed["description"]:
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 0)
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        "<:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(after, 0, 0)
                    return
            except KeyError:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or not self.bot.state
            or (message.interaction and message.interaction.user != self.bot.user)
        ):
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            # Color match
            try:
                if (
                    "Look at each color next to the words closely!"
                    in embed["description"]
                ):
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    options = {}
                    for line in embed["description"].splitlines()[1:]:
                        match_word = re.search("`(.+?)`", line)
                        match_color = re.search(":([^:]+):", line)
                        if match_word and match_color:
                            options[match_word.group(1)] = match_color.group(1)
                    await asyncio.sleep(6)
                    embed = message.embeds[0].to_dict()
                    word = re.search("`(.+?)`", embed["description"]).group(1)
                    color = options[word]
                    for count, button in enumerate(message.components[0].children):
                        if button.label == color:
                            await self.bot.click(message, 0, count)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    return
            except KeyError:
                pass

            # Emoji
            try:
                if "Look at the emoji closely!" in embed["description"]:
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    emoji = str(embed["description"].splitlines()[1])
                    await asyncio.sleep(4)
                    for row, i in enumerate(message.components):
                        for column, button in enumerate(i.children):
                            if str(button.emoji) == emoji:
                                await self.bot.click(message, row, column)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    return
            except KeyError:
                pass

            # Repeat order
            try:
                if any(
                    i in embed["description"]
                    for i in ["Repeat Order", "word order.", "words order"]
                ):
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    order = [
                        line[1:-1]
                        for line in message.embeds[0].description.splitlines()[1:6]
                    ]
                    await asyncio.sleep(6)
                    answers = {
                        button.label: i
                        for i, button in enumerate(message.components[0].children)
                    }
                    for choice in order:
                        await self.bot.click(message, 0, answers[choice])
                        await asyncio.sleep(0.5)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    return
            except KeyError:
                pass

            # Attack boss
            try:
                if "Attack the boss by clicking" in embed["description"]:
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    while not message.components[0].children[0].disabled:
                        await self.bot.click(message, 0, 0)
                        await asyncio.sleep(0.5)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    return
            except KeyError:
                pass

            # F in the chat
            try:
                if embed["description"] == "F":
                    await self.bot.click(message, 0, 0)
                    return
            except KeyError:
                pass

            # HighLow
            try:
                if "I just chose a secret number" in embed["description"]:
                    num = int(
                        (
                            re.search("\*\*(.*?)\*\*", embed["description"]).group(1)
                        ).title()
                    )
                    if num >= 50:
                        await self.bot.click(message, 0, 0)
                    else:
                        await self.bot.click(message, 0, 2)
                    return
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Minigames(bot))
