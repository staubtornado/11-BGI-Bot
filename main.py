import asyncio
import configparser
import difflib
import os

import discord
import dotenv
from discord import colour
from discord.ext import commands, tasks

version = 'a-0.0.1'

config = configparser.ConfigParser()
config.read('settings.cfg')

bot = commands.Bot(command_prefix = '/', owner_id = int(config.get('OWNER_SETTIGNS', 'owner_id'), base = 10), intents = discord.Intents.all())

dotenv.load_dotenv()
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print('Bot online...')

@bot.command(name='load')
@commands.is_owner()
async def load(ctx, extension):
    try:
        bot.load_extension(f"cogs.{extension}")
        await ctx.message.add_reaction('✅')
    except commands.ExtensionAlreadyLoaded:
        await ctx.message.add_reaction('❌')
    except commands.ExtensionNotFound:
        await ctx.message.add_reaction('❓')
    else:
        await ctx.message.add_reaction('✅')

@bot.command(name='unload')
@commands.is_owner()
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.message.add_reaction('✅')
    except commands.ExtensionNotLoaded:
        await ctx.message.add_reaction('❌')
    except commands.ExtensionNotFound:
        await ctx.message.add_reaction('❓')
    else:
        await ctx.message.add_reaction('✅')

@bot.command(name='reload')
@commands.is_owner()
async def reload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.message.add_reaction('✅')
    except commands.ExtensionNotLoaded:
        await ctx.message.add_reaction('❌')
    except commands.ExtensionNotFound:
        await ctx.message.add_reaction('❓')
    else:
        await ctx.message.add_reaction('✅')

CommandOnCooldown_check = []
CommandNotFound_check = []
Else_check = []

@bot.event
async def on_command_error(ctx, error):
    try:
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id in CommandOnCooldown_check:
                return
            else:
                try:
                    await ctx.send(embed = discord.Embed(title = 'Cooldown...', description = f'Der Command kann erst in {round(error.retry_after, 2)} Sekunden wieder ausgeführt werden.', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)) .set_footer(text = f'Verursacht durch {ctx.author} | Du kannst diese Nachricht erst nach dem Cooldown wiedersehen.'))
                except discord.Forbidden:
                    return
                else:
                    CommandOnCooldown_check.append(ctx.author.id)
                    await asyncio.sleep(error.retry_after)
                    CommandOnCooldown_check.remove(ctx.author.id)
                    return
            
        elif isinstance(error, commands.CommandNotFound):
            if ctx.author.id in CommandNotFound_check:
                return
            else:
                
                available_commands = []
                for command in bot.all_commands:
                    try:
                        if await(bot.get_command(command).can_run(ctx)) is True:
                            available_commands.append(command)
                    except Exception:
                        pass
                suggestion = ""
                similarity_search = difflib.get_close_matches(str(ctx.message.content)[4:], available_commands)
                for s in similarity_search:
                    suggestion += f'**-** `{ctx.prefix}{s}`\n'
                
                embed = discord.Embed(title = 'Befehl nicht gefunden...', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16))
                if suggestion != '':
                    embed.description = f'Wir konnten keine Befehle mit dem Namen `{str(ctx.message.content)[1:]}` finden. Villeicht meintest du:\n{suggestion}'
                else:
                    embed.description = f'Wir konnten keine Befehle mit dem Namen `{str(ctx.message.content)[1:]}` finden. Nutze `{ctx.prefix}help` für Hilfe.'
                
                try:
                    await ctx.send(embed = embed)
                except discord.Forbidden:
                    return
                else:
                    CommandNotFound_check.append(ctx.author.id)
                    await asyncio.sleep(10)
                    CommandNotFound_check.remove(ctx.author.id)
                    return

        else:
            if ctx.author.id in Else_check:
                return
            else:
                try:
                    await ctx.send(embed = discord.Embed(title = 'Unbekannter Fehler...', description = 'Ein unbekannter Fehler ist aufgetreten.', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)) .add_field(name = 'Details', value = str(error)))
                except discord.Forbidden:
                    return
                else:
                    Else_check.append(ctx.author.id)
                    await asyncio.sleep(10)
                    Else_check.remove(ctx.author.id)
                    return

    except Exception as err:
        return await ctx.send(embed = discord.Embed(title = 'Schwerwiegender Fehler', description = f'Ein schwerwiegender Fehler ist im Error-Handler ausgetreten. Fehlercode:\n`{error, err}`', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)))

bot.run(os.environ['DISCORD_BOT_TOKEN'])
