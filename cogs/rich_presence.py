import discord
from discord.ext import commands, tasks
import configparser

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

    @tasks.loop(seconds = 20)
    async def rich_presence_update(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'{config.get("BOT_SETTINGS", "prefix")}help | version: {version.get("BOT_VERSION", "latest_commit")}'))

def setup(bot):
    bot.add_cog(rich_presence(bot))