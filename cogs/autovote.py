import asyncio
import json
import random
import time

import requests
from discord.ext import commands, tasks


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.last_ran["auto_vote"] = 0
        self.vote.start()

    @tasks.loop(minutes=30)
    async def vote(self):
        if (
            time.time() - self.bot.last_ran["auto_vote"] < 43200
            or not self.bot.state
            or not self.bot.config_dict["auto_vote"]
        ):
            return

        await asyncio.sleep(random.randint(600, 1200))
        self.bot.last_ran["auto_vote"] = time.time()

        response = requests.post(
            "https://discord.com/api/v10/oauth2/authorize?client_id=477949690848083968&response_type=code&scope=identify",
            headers={"authorization": self.bot.config_dict["discord_token"]},
            json={"authorize": True, "permissions": 0},
        )
        code = json.loads(response.content.decode())["location"].split("code=")[-1]
        response = requests.get(f"https://discordbotlist.com/api/v1/oauth?code={code}")
        dbl_token = json.loads(response.content.decode())["token"]
        req = json.loads(
            requests.post(
                "https://discordbotlist.com/api/v1/bots/270904126974590976/upvote",
                headers={"authorization": dbl_token},
            ).content.decode()
        )


async def setup(bot):
    await bot.add_cog(Vote(bot))
