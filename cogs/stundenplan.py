import configparser
import datetime

import discord
from discord.embeds import Embed
import pytz
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

config = configparser.ConfigParser()
config.read('settings.cfg')

async def get_stundenplan():
    timezone = pytz.timezone("CET")
    current_time = datetime.datetime.ctime(datetime.datetime.now(timezone))
    week_number = datetime.datetime.now(timezone).isocalendar()[1]

    if week_number % 2 == 0:
        odd_or_even = 'gerade'
    else:
        odd_or_even = 'ungerade'

    return (Embed(title = 'Stundenplan', description = 'Aktueller Stundenplan der 11 BGI.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) 
        .add_field(name = 'Zuletzt aktualisiert', value = current_time) 
        .add_field(name = 'Woche', value = f'Diese Woche ist `{odd_or_even}`.') 
        .set_footer(text = 'Angaben ohne Gewähr') 
        .set_image(url = 'https://media.discordapp.net/attachments/883364257364844615/883364663394451556/unknown.png'))

class stundenplan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stundenplan_update_task.start()

    def cog_unload(self):
        self.stundenplan_update_task.cancel()

    @tasks.loop(minutes = 30)
    async def stundenplan_update_task(self):
        await self.bot.wait_until_ready()
        
        channel = self.bot.get_channel(882652054005379143)
        message = await channel.fetch_message(883365699416907786)

        return await message.edit(embed = await(get_stundenplan()))
    
    @commands.command(name = 'stundenplan')
    @commands.cooldown(1, 5, type = BucketType.default)
    async def function_stundenplan(self, ctx):
        return await ctx.send(embed = await(get_stundenplan()))

def setup(bot):
    bot.add_cog(stundenplan(bot))
