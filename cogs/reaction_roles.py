import configparser
import platform

import discord
import psutil
from discord.embeds import Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

kurswahl_reaction_message_id = 886181942544982087
gamewahl_reaction_message_id = 886306275422519356

config = configparser.ConfigParser()
config.read('settings.cfg')


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='systeminfo')
    @commands.cooldown(2, 5, type=BucketType.default)
    async def systeminfo(self, ctx):

        embed = Embed(title='System Informationen',
                      description='Informationen über die Hardware, auf dem der Bot läuft.',
                      colour=int(config.get('COLOUR_SETTINGS', 'standart'), base=16))

        embed.add_field(name='Python Version', value=platform.python_version(), inline=True)
        embed.add_field(name='discord.py Version', value=discord.__version__, inline=True)
        embed.add_field(name='System', value=platform.system(), inline=True)
        embed.add_field(name='Release / Version', value=f'{platform.release()} / {platform.version()}', inline=True)
        embed.add_field(name='Processor', value=platform.processor(), inline=True)
        embed.add_field(name='RAM',
                        value=f'{round(psutil.virtual_memory().used / (1024.0 ** 3), 2)}GB / {round(psutil.virtual_memory().total / (1024.0 ** 3), 2)}GB',
                        inline=True)
        return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == kurswahl_reaction_message_id:
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
        elif payload.message_id == gamewahl_reaction_message_id:
            if payload.emoji.name == 'leagueoflegends':
                role_id = 884827409843638382
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == 'Minecraft':
                role_id = 884827761280180276
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == 'gta5':
                role_id = 884827581713616988
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)
            elif payload.emoji.name == 'cod':
                role_id = 884827504559398962
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                return await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        if payload.message_id == kurswahl_reaction_message_id:
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
        elif payload.message_id == gamewahl_reaction_message_id:
            if payload.emoji.name == 'leagueoflegends':
                role_id = 884827409843638382
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == 'Minecraft':
                role_id = 884827761280180276
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == 'gta5':
                role_id = 884827581713616988
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)
            elif payload.emoji.name == 'cod':
                role_id = 884827504559398962
                role = discord.utils.get(guild.roles, id=role_id)
                return await member.remove_roles(role)

    @commands.command(name='kurswahl',
                      description='Ein Befehl, der es Nutzern erlaubt, sich auf dem Discordserver in Kurse einzuwählen.')
    async def function_kurswahl(self, ctx):
        message = await ctx.send(
            embed=discord.Embed(title='Kursauswahl', description='Erhalte Zugriff auf kursspezifische Channel.',
                                colour=int(config.get('COLOUR_SETTINGS', 'standart'), base=16))
            .add_field(name='Spanisch', value='🇪🇸')
            .add_field(name='Ev. Religion', value='⛪')
            .add_field(name='Kt. Religion', value='✝️')
            .add_field(name='Ethik', value='☁️')
            )
        reactions = ['🇪🇸', '⛪', '✝️', '☁️']
        for reaction in reactions:
            await message.add_reaction(reaction)

    @commands.command(name='gamewahl')
    async def function_gaming_wahl(self, ctx):
        message = await ctx.send(
            embed=Embed(title='Gamewahl', description='Erhalte Zugriff auf gamespezifische Channel.',
                        colour=int(config.get('COLOUR_SETTINGS', 'standart'), base=16))
            .add_field(name='League of Legends', value='<:leagueoflegends:886292690269003826>')
            .add_field(name='Grand Theft Auto V', value='<:gta5:886294793976709180>')
            .add_field(name='Minecraft', value='<:Minecraft:886295237578879017>')
            .add_field(name='Call of Duty', value='<:cod:886297203449147402>'))

        reactions = ['<:leagueoflegends:886292690269003826>', '<:gta5:886294793976709180>',
                     '<:Minecraft:886295237578879017>', '<:cod:886297203449147402>']
        for reaction in reactions:
            await message.add_reaction(reaction)


def setup(bot):
    bot.add_cog(System(bot))
