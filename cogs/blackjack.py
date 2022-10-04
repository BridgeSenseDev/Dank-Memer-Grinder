import asyncio
import json
import random
import re
import threading

from discord.ext import commands, tasks


def update():
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


def bj_formula(embed):
    player_sum = []
    dealer_sum = []
    for i in re.findall("\[`(.*?)`]", embed.to_dict()["fields"][0]["value"]):
        try:
            player_sum.append(int(i[2:]))
        except:
            if i[2:] in ["K", "Q", "J"]:
                player_sum.append(10)
            elif i[2:] == "A":
                player_sum.append(11)
    for i in re.findall("\[`(.*?)`]", embed.to_dict()["fields"][1]["value"]):
        try:
            dealer_sum.append(int(i[2:]))
        except:
            if i[2:] in ["K", "Q", "J"]:
                dealer_sum.append(10)
            elif i[2:] == "A":
                dealer_sum.append(11)
    return bj_optimizer(player_sum, dealer_sum)


def bj_optimizer(player_sum, dealer_sum):
    if 11 in player_sum:
        player_hand = len(player_sum)
        player_sum = sum(player_sum)
        dealer_sum = sum(dealer_sum)
        if player_sum <= 17:
            return 0
        if player_sum == 18:
            if dealer_sum in [3, 4, 5, 6]:
                return 0
            elif player_hand >= 3:
                return 0
            elif player_hand <= 2:
                return 1
        if player_sum == 19:
            if dealer_sum != 10 and player_hand >= 4:
                return 0
            elif dealer_sum != 10 and player_hand <= 3:
                return 1
            elif player_hand >= 3:
                return 0
            elif player_hand <= 2:
                return 1
        if player_sum >= 20:
            if player_hand >= 4:
                return 0
            else:
                return 1
    else:
        player_hand = len(player_sum)
        player_sum = sum(player_sum)
        dealer_sum = sum(dealer_sum)
        if player_sum <= 11:
            return 0
        if player_sum == 12:
            if dealer_sum not in [4, 5, 6]:
                return 0
            elif player_hand >= 3:
                return 0
            else:
                return 1
        if player_sum == 13:
            if dealer_sum >= 7:
                return 0
            if dealer_sum in [4, 5, 6] and player_hand >= 4:
                return 0
            elif dealer_sum in [4, 5, 6] and player_hand <= 3:
                return 1
            if dealer_sum in [2, 3] and player_hand >= 3:
                return 0
            elif dealer_sum in [2, 3] and player_hand <= 2:
                return 1
        if player_sum == 14 or player_sum == 15:
            if dealer_sum >= 7:
                return 0
            if dealer_sum <= 6 and player_hand >= 4:
                return 0
            elif dealer_sum <= 6 and player_hand <= 3:
                return 1
        if player_sum == 16:
            if dealer_sum >= 7:
                return 0
            if dealer_sum in [4, 5, 6]:
                return 1
            if dealer_sum in [2, 3] and player_hand >= 4:
                return 0
            elif dealer_sum in [2, 3] and player_hand <= 3:
                return 1
        if player_sum == 17:
            if dealer_sum <= 8:
                return 1
            if dealer_sum >= 9 and player_hand >= 4:
                return 0
            elif dealer_sum >= 9 and player_hand <= 3:
                return 1
        if player_sum >= 18:
            return 1


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.multipliers.start()
        self.bj.start()

    @tasks.loop(seconds=20)
    async def bj(self):
        try:
            if (
                config_dict["commands"]["bj"]["state"] is True
                and config_dict["state"] is True
            ):
                try:
                    if multi <= int(config_dict["commands"]["bj"]["multi"]):
                        self.bot.window.ui.output.append(
                            "Not blackjacking because multipliers is lower than"
                            f" {int(config_dict['commands']['bj']['multi'])}"
                        )
                        return
                except:
                    self.bot.window.ui.output.append(
                        "Not blackjacking because multipliers required"
                        f" ({config_dict['commands']['bj']['multi']}) is not a number"
                    )
                    return
                await asyncio.sleep(random.randint(0, 3))
                await self.bot.channel.send(
                    f"pls bj {config_dict['commands']['-bj-']['-bjamount-']}"
                )
        except KeyError:
            pass

    @bj.before_loop
    async def before_bj(self):
        await asyncio.sleep(10)

    @tasks.loop(minutes=3)
    async def multipliers(self):
        if (
            config_dict["commands"]["bj"]["state"] is True
            and config_dict["state"] is True
        ):
            async for cmd in self.bot.channel.slash_commands(
                command_ids=[1011560371171102766]
            ):
                await cmd()
                break

    @commands.Cog.listener()
    async def on_message(self, message):
        global multi
        if message.channel.id != self.bot.channel_id or config_dict["state"] is False:
            return

        for embed in message.embeds:
            try:
                if "Your Multipliers" in embed.to_dict()["title"]:
                    multi = int(
                        (
                            re.search("Total: `(.*?)%`", embed.to_dict()["description"])
                        ).group(1)
                    )
            except KeyError:
                pass
            try:
                if (
                    "blackjack game" in embed.to_dict()["author"]["name"]
                    and config_dict["commands"]["bj"]["state"] is True
                ):
                    await message.components[0].children[bj_formula(embed)].click()
            except KeyError:
                pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.channel.id != self.bot.channel_id:
            return
        embeds = after.embeds
        for embed in embeds:
            try:
                if (
                    "blackjack game" in embed.to_dict()["author"]["name"]
                    and config_dict["commands"]["bj"]["state"] is True
                ):
                    if "description" not in embed.to_dict():
                        await after.components[0].children[bj_formula(embed)].click()
                    elif any(
                        i in embed.to_dict()["description"]
                        for i in ["Tied.", "Lost.", "Won"]
                    ):
                        await after.components[0].children[2].click()
            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
