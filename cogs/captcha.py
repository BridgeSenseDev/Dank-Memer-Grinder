import asyncio

from discord.ext import commands


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or not self.bot.state:
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            try:
                if "CAPTCHA" not in embed["title"]:
                    return

                # Matching image captcha
                if "matching image" in embed["description"]:
                    captcha_url = embed["image"]["url"]
                    for count, button in enumerate(message.components[0].children):
                        if button.emoji.url in captcha_url:
                            await asyncio.sleep(0.5)
                            await self.bot.click(message, 0, count)
                            return

                # Pepe captcha
                if "pepe" in embed["description"]:
                    for row, i in enumerate(message.components):
                        for column, button in enumerate(i.children):
                            if not hasattr(button, "id"):
                                continue
                            if button.emoji.id in [
                                819014822867894304,
                                796765883120353280,
                                860602697942040596,
                                860602923665588284,
                                860603013063507998,
                                936007340736536626,
                                933194488241864704,
                                680105017532743700,
                            ]:
                                await asyncio.sleep(0.3)
                                await self.bot.click(message, row, column)
                                continue

            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Captcha(bot))
