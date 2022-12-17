import re
import asyncio
from discord.ext import commands


class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            # MoleMan
            try:
                if "Dodge the Worms!" in embed["description"]:
                    print("moleman")
                    print(embed["description"])
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if (
                        "<:emptyspace:827651824739156030><:Worm:864261394920898600>"
                        "<:Worm:864261394920898600>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 0)
                    elif (
                        "<:Worm:864261394920898600><:emptyspace:827651824739156030>"
                        "<:Worm:864261394920898600>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 1)
                    elif (
                        "<:Worm:864261394920898600><:Worm:864261394920898600>"
                        "<:emptyspace:827651824739156030>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 3)
            except KeyError:
                pass

            # Football
            try:
                if "Hit the ball!" in embed["description"]:
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if ":levitate:" == embed["description"].splitlines()[2]:
                        await self.bot.click(message, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>:levitate:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 0)
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:levitate:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 1)
                    return
            except KeyError:
                pass

            # Color match
            try:
                if (
                    "Look at each color next to the words closely!"
                    in embed["description"]
                ):
                    options = {
                        str(
                            re.search(
                                "`(.*?)`",
                                embed["description"].splitlines()[1],
                            ).group(1)
                        ): str(
                            re.search(
                                ":(.*?):",
                                embed["description"].splitlines()[1],
                            ).group(1)
                        ),
                        str(
                            re.search(
                                "`(.*?)`",
                                embed["description"].splitlines()[2],
                            ).group(1)
                        ): str(
                            re.search(
                                ":(.*?):",
                                embed["description"].splitlines()[2],
                            ).group(1)
                        ),
                        str(
                            re.search(
                                "`(.*?)`",
                                embed["description"].splitlines()[3],
                            ).group(1)
                        ): str(
                            re.search(
                                ":(.*?):",
                                embed["description"].splitlines()[3],
                            ).group(1)
                        ),
                    }
                    await asyncio.sleep(6)
                    embed = message.embeds[0].to_dict()
                    word = re.search("`(.*?)`", embed["description"]).group(1)
                    color = options[word]
                    for count, i in enumerate(message.components[0].children):
                        if i.label == color:
                            await self.bot.click(message, 0, count)
                    return
            except KeyError:
                pass

            # Emoji
            try:
                if "Look at the emoji closely!" in embed["description"]:
                    emoji = str(embed["description"].splitlines()[1])
                    await asyncio.sleep(4)
                    for count, i in enumerate(message.components[0].children):
                        if str(i.emoji) == emoji:
                            await self.bot.click(message, 0, count)
                            return
                    for count, i in enumerate(message.components[1].children):
                        if str(i.emoji) == emoji:
                            await self.bot.click(message, 1, count)
                        return
            except KeyError:
                pass

            # Repeat order
            try:
                if any(
                    i in embed["description"]
                    for i in ["Repeat Order", "word order.", "words order"]
                ):
                    order = [
                        str(embed["description"].splitlines()[1])[1:-1],
                        str(embed["description"].splitlines()[2])[1:-1],
                        str(embed["description"].splitlines()[3])[1:-1],
                        str(embed["description"].splitlines()[4])[1:-1],
                        str(embed["description"].splitlines()[5])[1:-1],
                    ]
                    await asyncio.sleep(6)
                    answers = {
                        str(message.components[0].children[0].label): 0,
                        str(message.components[0].children[1].label): 1,
                        str(message.components[0].children[2].label): 2,
                        str(message.components[0].children[3].label): 3,
                        str(message.components[0].children[4].label): 4,
                    }
                    for i in order:
                        await self.bot.click(message, 0, answers[i])
                        await asyncio.sleep(0.7)
                    return
            except KeyError:
                pass

            # Attack boss
            try:
                if "Attack the boss by clicking" in embed["description"]:
                    x = 16
                    try:
                        while x >= 0:
                            await self.bot.click(message, 0, 0)
                            await asyncio.sleep(0.5)
                            x -= 1
                        return
                    except KeyError:
                        return
            except KeyError:
                pass

            # Basketball
            try:
                if "Dunk the ball!" in embed["description"]:
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>:basketball:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>:basketball:"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 1)
                    elif ":basketball:" == embed["description"].splitlines()[2]:
                        await self.bot.click(message, 0, 0)
                    return
            except KeyError:
                pass

            # F in the chat
            try:
                if embed["description"] == "F":
                    await self.bot.click(message, 0, 0)
            except KeyError:
                pass

            # Dragon
            try:
                if "Dodge the Fireball" in embed["description"]:
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 1)
                    elif (
                        "<:emptyspace:827651824739156030><:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 0)
                    elif (
                        "<:FireBall:883714770748964864>"
                        == embed["description"].splitlines()[2]
                    ):
                        await self.bot.click(message, 0, 2)
            except KeyError:
                pass

            # Catch the fish
            try:
                if "Catch the fish!" in embed["description"]:
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030>"
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 1)
                    elif (
                        "<a:LegendaryFish:971430841211322408>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 0)
                    await asyncio.sleep(2)
                    embed = message.embeds[0].to_dict()
                    if (
                        "<:emptyspace:827651824739156030>"
                        "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 2)
                    elif (
                        "<:emptyspace:827651824739156030><:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 1)
                    elif (
                        "<:Kraken:860228238956429313>"
                        == embed["description"].splitlines()[1]
                    ):
                        await self.bot.click(message, 0, 0)
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Minigames(bot))
