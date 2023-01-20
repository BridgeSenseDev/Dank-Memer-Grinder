from discord.ext import commands


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or self.bot.config_dict[self.bot.account_id]["state"] is False
        ):
            return

        for embed in message.embeds:
            embed = embed.to_dict()
            try:
                if "CAPTCHA" not in embed["title"]:
                    return

                # Matching image captcha
                if "matching image" in embed["description"]:
                    captcha = embed.image.url
                    for count, i in enumerate(message.components):
                        if i.emoji.url in captcha:
                            await self.bot.click(message, 0, count)
                            break

                # Pepe captcha
                if "pepe" in embed["description"]:
                    for count, i in enumerate(message.components):
                        if i.emoji.id in [
                            819014822867894304,
                            796765883120353280,
                            860602697942040596,
                            860602923665588284,
                            860603013063507998,
                            936007340736536626,
                            933194488241864704,
                            680105017532743700,
                        ]:
                            await self.bot.click(message, 0, count)
                            break

            except KeyError:
                pass


async def setup(bot):
    await bot.add_cog(Captcha(bot))
