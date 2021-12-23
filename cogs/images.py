import configparser
import requests

from discord.embeds import Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

# from urlparse import urlsplit
# from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('settings.cfg')


class Bilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='klassenfoto', aliases=['klasse'])
    @commands.cooldown(2, 5, type=BucketType.default)
    async def klassenfoto(self, ctx):
        return await ctx.send(
            embed=Embed(title='Klassenfoto', description='Klassenfoto der 11 BGI von <t:1631095200:R>.', colour=int(
                config.get('COLOUR_SETTINGS', 'standard'), base=16))
                .set_image(
                url='https://media.discordapp.net/attachments/827625662369890354/903961782836674580'
                    '/PXL_20211030_105907975.jpg?width=632&height=468'))

    @commands.command(name="adventskalender", aliases=['advent', "NNN"])
    async def adventskalender(self, ctx):
        return await ctx.send(embed=Embed(title="Adventskalender", description="Advent, Advent, das Nüsslein brennt.",
                                          colour=int(
                                              config.get('COLOUR_SETTINGS', 'standard'), base=16))
                              .set_image(url="https://media.discordapp.net/attachments/883364257364844615"
                                             "/918883651574444032/PXL_20211210_101220199_1.jpg?width=562&height=749"))

    @commands.command(name='meme')
    async def meme(self, ctx):
        redditPage = 'https://www.reddit.com/r/ich_iel/'
        result = requests.get(redditPage)
        print(result.content)


def setup(bot):
    bot.add_cog(Bilder(bot))
