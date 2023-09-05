import asyncio
import contextlib
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

        for embed in before.embeds:
            embed = embed.to_dict()
            after_embed = after.embeds[0].to_dict()

            # Moleman
            with contextlib.suppress(KeyError):
                if (
                    "Dodge the Worms!" in embed["description"]
                    and "Mole Man" in after_embed["description"]
                ):
                    self.bot.log("Solved Dodge Worms Minigame", "green")
                elif (
                    "Dodge the Worms!" in embed["description"]
                    and "Dodge the Worms!" not in after_embed["description"]
                ):
                    self.bot.log("Failed Dodge Worms Minigame", "red")

        for embed in after.embeds:
            embed = embed.to_dict()

            # MoleMan
            with contextlib.suppress(KeyError):
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
            # Football
            with contextlib.suppress(KeyError):
                if "Hit the ball!" in embed["description"]:
                    self.bot.log("Solving Football Minigame", "yellow")
                    if embed["description"].splitlines()[2] == ":levitate:":
                        await self.bot.click(after, 0, 2, [0, 0])
                    elif (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030>:levitate:"
                    ):
                        await self.bot.click(after, 0, 0, [0, 0])
                    if (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:levitate:"
                    ):
                        await self.bot.click(after, 0, 1, [0, 0])
                    self.bot.log("Solved Football Minigame", "green")
                    return
            # Basketball
            with contextlib.suppress(KeyError):
                if "Dunk the ball!" in embed["description"]:
                    self.bot.log("Solving Basketball Minigame", "yellow")
                    if (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:basketball:"
                    ):
                        await self.bot.click(after, 0, 2, [0, 0])
                    elif (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030>:basketball:"
                    ):
                        await self.bot.click(after, 0, 1)
                    elif embed["description"].splitlines()[2] == ":basketball:":
                        await self.bot.click(after, 0, 0, [0, 0])
                    self.bot.log("Solved Basketball Minigame", "green")
                    return
            # Dragon
            with contextlib.suppress(KeyError):
                if "Dodge the Fireball" in embed["description"]:
                    self.bot.log("Solving Dragon Minigame", "yellow")
                    if (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        embed["description"].splitlines()[2]
                        == "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                    ):
                        await self.bot.click(after, 0, 0)
                    elif (
                        embed["description"].splitlines()[2]
                        == "<:FireBall:883714770748964864>"
                    ):
                        await self.bot.click(after, 0, 2)
                    self.bot.log("Solved Dragon Minigame", "green")
                    return
            # Catch the fish
            with contextlib.suppress(KeyError):
                if "Catch the fish!" in embed["description"]:
                    self.bot.log("Solving Fish Minigame", "yellow")
                    if (
                        embed["description"].splitlines()[1]
                        == "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                    ):
                        await self.bot.click(after, 0, 2)
                    elif (
                        embed["description"].splitlines()[1]
                        == "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        embed["description"].splitlines()[1]
                        == "<a:LegendaryFish:971430841211322408>"
                    ):
                        await self.bot.click(after, 0, 0)
                    if (
                        embed["description"].splitlines()[1]
                        == "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                    ):
                        await self.bot.click(after, 0, 2)
                    elif (
                        embed["description"].splitlines()[1]
                        == "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                    ):
                        await self.bot.click(after, 0, 1)
                    elif (
                        embed["description"].splitlines()[1]
                        == "<:Kraken:860228238956429313>"
                    ):
                        await self.bot.click(after, 0, 0)
                    self.bot.log("Solved Fish Minigame", "green")
                    return

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
            with contextlib.suppress(KeyError):
                if "Dodge the Worms!" in embed["description"]:
                    self.bot.log("Solving Dodge Worms Minigame", "yellow")

            # Color match
            with contextlib.suppress(KeyError):
                if (
                    "Look at each color next to the words closely!"
                    in embed["description"]
                ):
                    self.bot.log("Solving Color Match Minigame", "yellow")
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    options = {}
                    for line in embed["description"].splitlines()[1:]:
                        match_word = re.search("`(.+?)`", line)
                        match_color = re.search(":([^:]+):", line)
                        if match_word and match_color:
                            options[match_word[1]] = match_color[1]
                    await asyncio.sleep(6)
                    embed = message.embeds[0].to_dict()
                    word = re.search("`(.+?)`", embed["description"])[1]
                    color = options[word]
                    for count, button in enumerate(message.components[0].children):
                        if button.label == color:
                            await self.bot.click(message, 0, count)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    self.bot.log("Solved Color Match Minigame", "green")
                    return

            # Emoji
            with contextlib.suppress(KeyError):
                if "Look at the emoji closely!" in embed["description"]:
                    self.bot.log("Solving Emoji Minigame", "yellow")
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
                    self.bot.log("Solved Emoji Minigame", "green")
                    return
            # Repeat order
            with contextlib.suppress(KeyError):
                if any(
                    i in embed["description"]
                    for i in ["Repeat Order", "word order.", "words order"]
                ):
                    self.bot.log("Solving Repeat Order Minigame", "yellow")
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
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    self.bot.log("Solved Repeat Order Minigame", "green")
                    return
            # Attack boss
            with contextlib.suppress(KeyError):
                if "Attack the boss by clicking" in embed["description"]:
                    self.bot.log("Solving Attack Boss Minigame", "yellow")
                    self.bot.last_ran = {
                        k: v + 100 if v != 0 else float("inf")
                        for k, v in self.bot.last_ran.items()
                    }
                    while not message.components[0].children[0].disabled:
                        await self.bot.click(message, 0, 0)
                    self.bot.last_ran = {
                        k: v - 100 if v != float("inf") else 0
                        for k, v in self.bot.last_ran.items()
                    }
                    self.bot.log("Solved Attack Boss Minigame", "green")
                    return
            # F in the chat
            with contextlib.suppress(KeyError):
                if embed["description"] == "F":
                    self.bot.log("Solving F In The Chat Minigame", "yellow")
                    await self.bot.click(message, 0, 0)
                    self.bot.log("Solved F In The Chat Minigame", "green")
                    return
            # HighLow
            with contextlib.suppress(KeyError):
                if "I just chose a secret number" in embed["description"]:
                    num = int(
                        re.search("\*\*(.*?)\*\*", embed["description"])[1].title()
                    )
                    if num >= 50:
                        await self.bot.click(message, 0, 0)
                    else:
                        await self.bot.click(message, 0, 2)
                    return


async def setup(bot):
    await bot.add_cog(Minigames(bot))
