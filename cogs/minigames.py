import threading
import re
import json
import asyncio
from discord.ext import commands


def update():
    global commands_dict
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
    with open("commands.json", "r") as commands_file:
        commands_dict = json.load(commands_file)


update()


class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return

        # F in the chat
        if message.content == "F" and message.author.id == 270904126974590976:
            await message.components[0].children[0].click()
            return

        # Dragon
        if "Dodge the Fireball" in message.content:
            "Caught Dragon"
            await asyncio.sleep(2)
            if "              <:FireBall:883714770748964864>" == message.content.splitlines()[2]:
                await message.components[0].children[1].click()
            elif "       <:FireBall:883714770748964864>" == message.content.splitlines()[2]:
                await message.components[0].children[0].click()
            elif "<:FireBall:883714770748964864>" == message.content.splitlines()[2]:
                await message.components[0].children[2].click()
            return

        # Catch the fish
        if "Catch the fish!" in message.content:
            await asyncio.sleep(2)
            if "              <:legendaryfish:714981071548186684>" == message.content.splitlines()[1]:
                await message.components[0].children[2].click()
            elif "       <:legendaryfish:714981071548186684>" == message.content.splitlines()[1]:
                await message.components[0].children[1].click()
            elif "<:legendaryfish:714981071548186684>" == message.content.splitlines()[1]:
                await message.components[0].children[0].click()
            await asyncio.sleep(2)
            if "              <:Kraken:860228238956429313>" == message.content.splitlines()[1]:
                await message.components[0].children[2].click()
            elif "       <:Kraken:860228238956429313>" == message.content.splitlines()[1]:
                await message.components[0].children[1].click()
            elif "<:Kraken:860228238956429313>" == message.content.splitlines()[1]:
                await message.components[0].children[0].click()
            return

        for embed in message.embeds:
            print(embed.to_dict())
            # Football
            try:
                if "Hit the ball!" in embed.to_dict()["description"]:
                    await asyncio.sleep(2)
                    print(embed.to_dict()["description"])
                    if ":levitate:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[2].click()
                    elif "       :levitate:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[0].click()
                    if "              :levitate:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[1].click()
                    return
            except KeyError:
                pass

            # Color match
            try:
                if "Look at each color next to the words closely!" in embed.to_dict()["description"]:
                    options = {str(re.search("`(.*?)`", embed.to_dict()["description"].splitlines()[1]).group(1)): str(
                        re.search(":(.*?):",embed.to_dict()["description"].splitlines()[1]).group(1)),
                        str(re.search("`(.*?)`", embed.to_dict()["description"].splitlines()[2]).group(1)): str(
                            re.search(":(.*?):", embed.to_dict()["description"].splitlines()[2]).group(1)),
                        str(re.search("`(.*?)`", embed.to_dict()["description"].splitlines()[3]).group(1)): str(
                            re.search(":(.*?):", embed.to_dict()["description"].splitlines()[3]).group(1))}
                    await asyncio.sleep(6)
                    word = re.search("`(.*?)`", embed.to_dict()["description"]).group(1)
                    color = options[word]
                    print(color)
                    for i in message.components[0].children:
                        print(i.label)
                    return
            except:
                pass

            # Emoji
            try:
                if "Look at the emoji closely!" in embed.to_dict()["description"]:
                    emoji = str(embed.to_dict()["description"].splitlines()[1])
                    await asyncio.sleep(4)
                    for i in message.components[0].children + message.components[1].children:
                        if str(i.emoji) == emoji:
                            await i.click()
                    return
            except:
                pass

            # Repeat order
            try:
                if any(i in embed.to_dict()["description"] for i in ["Repeat Order", "word order.", "words order"]):
                    order = [str(embed.to_dict()["description"].splitlines()[1])[1:-1], str(embed.to_dict()["description"].splitlines()[2])[1:-1],
                             str(embed.to_dict()["description"].splitlines()[3])[1:-1], str(embed.to_dict()["description"].splitlines()[4])[1:-1],
                             str(embed.to_dict()["description"].splitlines()[5])[1:-1]]
                    await asyncio.sleep(6)
                    print(order)
                    answers = {str(message.components[0].children[0].label): 0,
                               str(message.components[0].children[1].label): 1,
                               str(message.components[0].children[2].label): 2,
                               str(message.components[0].children[3].label): 3,
                               str(message.components[0].children[4].label): 4}
                    for i in order:
                        await message.components[0].children[int(answers[i])].click()
                        await asyncio.sleep(0.7)
                    return
            except:
                pass

            # Attack boss
            try:
                if "Attack the boss by clicking" in embed.to_dict()["description"]:
                    x = 16
                    try:
                        while x >= 0:
                            await message.components[0].children[0].click()
                            await asyncio.sleep(0.5)
                            x -= 1
                        return
                    except:
                        return
            except:
                pass

            # Basketball
            try:
                if "Dunk the ball!" in embed.to_dict()["description"]:
                    await asyncio.sleep(2)
                    if "              :basketball:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[2].click()
                    elif "       :basketball:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[1].click()
                    elif ":basketball:" == embed.to_dict()["description"].splitlines()[2]:
                        await message.components[0].children[0].click()
                    return
            except:
                pass


async def setup(bot):
    await bot.add_cog(Minigames(bot))
