import discord
from discord.ext import commands
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 884877998736683088:
            if payload.emoji.name == '🇪🇸':
                return await payload.member.d
    
    @commands.command(name = 'kurswahl', description = 'Ein Befehl, der es Nutzern erlaubt, sich auf dem Discordserver in Kurse einzuwählen.')
    async def function_kurswahl(self, ctx):
        await ctx.send(embed = discord.Embed(title = 'Kursauswahl', description = 'Erhalte Zugriff auf Kurse, indem du mit den jeweils zugehörigen Emojis reagierst. Zum Verlassen, Reaktion entfernen.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)))



def setup(bot):
    bot.add_cog(reaction_roles(bot))