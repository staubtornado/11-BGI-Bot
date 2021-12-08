import discord
from discord.ext import commands, tasks
import configparser
import datetime

version = configparser.ConfigParser()
version.read('version.cfg')

config = configparser.ConfigParser()
config.read('settings.cfg')


class rich_presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rich_presence_update.start()

    def cog_unload(self):
        self.rich_presence_update.cancel()

    @tasks.loop(seconds=20)
    async def rich_presence_update(self):
        ferien = datetime.datetime(2021, 12, 23, 10, 15)
        heute = datetime.datetime.today().replace(microsecond=0)

        await self.bot.wait_until_ready()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                 name=f'{ferien - heute}'))


def setup(bot):
    bot.add_cog(rich_presence(bot))
