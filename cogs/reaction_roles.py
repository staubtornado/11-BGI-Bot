import discord
from discord.ext import commands
import configparser

reaction_message_id = 886181942544982087

config = configparser.ConfigParser()
config.read('settings.cfg')

class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == reaction_message_id:
            if payload.emoji.name == '🇪🇸':
                role_id = 884830841543467009
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == '⛪':
                role_id = 884830877467697213
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == '✝️':
                role_id = 884830916390817832
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == '☁️':
                role_id = 884830949580349451
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        if payload.message_id == reaction_message_id:
            if payload.emoji.name == '🇪🇸':
                role_id = 884830841543467009
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == '⛪':
                role_id = 884830877467697213
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == '✝️':
                role_id = 884830916390817832
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == '☁️':
                role_id = 884830949580349451
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
    
    @commands.command(name = 'kurswahl', description = 'Ein Befehl, der es Nutzern erlaubt, sich auf dem Discordserver in Kurse einzuwählen.')
    async def function_kurswahl(self, ctx):
        message = await ctx.send(embed = discord.Embed(title = 'Kursauswahl', description = 'Erhalte Zugriff auf kursspezifische Channel.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16))
        .add_field(name = 'Spanisch', value = '🇪🇸')
        .add_field(name = 'Ev. Religion', value = '⛪')
        .add_field(name = 'Kt. Religion', value = '✝️')
        .add_field(name = 'Ethik', value = '☁️')
        )
        reactions = ['🇪🇸', '⛪', '✝️', '☁️']
        for reaction in reactions:
            await message.add_reaction(reaction)

def setup(bot):
    bot.add_cog(reaction_roles(bot))