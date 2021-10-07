import asyncio
import configparser
import difflib
import os
import shutil
import stat
import subprocess
import sys
import time

import discord
import dotenv
import git
from discord.embeds import Embed
from discord.ext import commands, tasks
from github import Github

version = configparser.ConfigParser()
version.read('version.cfg')

config = configparser.ConfigParser()
config.read('settings.cfg')
dotenv.load_dotenv()

class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = Embed(title="Hilfe")
        for cog, commands in mapping.items():
           command_signatures = [self.get_command_signature(c) for c in commands]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

bot = commands.Bot(command_prefix = config.get('BOT_SETTINGS', 'prefix'), owner_id = int(config.get('OWNER_SETTIGNS', 'owner_id'), base = 10), intents = discord.Intents.all(), help_command = MyHelpCommand())
github = Github(os.environ['GITHUB_API_TOKEN'])

@tasks.loop(minutes = 30)
async def github_update_check():
    if version.get('BOT_VERSION', 'latest_commit') == str(github.get_repo('Staubtornado/11-BGI-Bot').pushed_at):
        return
    else:
        print('Update found. Preparing update to the newest version...\nClearing content of update folder...')

        def on_rm_error(func, path, exc_info):
            print(f'{func}{path} {exc_info}')
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        shutil.rmtree(f'{os.getcwd()}{os.sep}update{os.sep}11-BGI-Bot{os.sep}', onerror = on_rm_error)
        
        print('Downloading the newest update...')
        git.Git(f"{os.getcwd()}{os.sep}update").clone("https://github.com/Staubtornado/11-BGI-Bot.git")
        print('Update downloaded. Applying changes...')
        shutil.rmtree(f'{os.getcwd()}{os.sep}update{os.sep}11-BGI-Bot{os.sep}.git', onerror = on_rm_error)
        
        root_src_dir = f'{os.getcwd()}{os.sep}update{os.sep}11-BGI-Bot{os.sep}'
        root_dst_dir = os.getcwd()

        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    if os.path.samefile(src_file, dst_file):
                        continue
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)

        version.set('BOT_VERSION', 'latest_commit', str(github.get_repo('Staubtornado/11-BGI-Bot').pushed_at))

        with open('version.cfg', 'w') as conf:
            version.write(conf)

        print('Update successful. Restarting script...')
        os.system(f'python{str(sys.version)[:-1]} {__file__}')  
        time.sleep(0.2)
        quit()
github_update_check.start()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'Bot running with the latest update, published on {version.get("BOT_VERSION", "latest_commit")}')

@bot.command(name='hahaa')
async def haha(ctx):
    return await ctx.send('Haha')

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
    except commands.ExtensionNotFound:
        await ctx.message.add_reaction('❓')
    except commands.ExtensionNotLoaded:
        await ctx.message.add_reaction('❌')
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
                    await ctx.send(embed = discord.Embed(title = 'Cooldown...', description = f'Der Befehl kann erst in {round(error.retry_after, 2)} Sekunden wieder ausgeführt werden.', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)) .set_footer(text = f'Verursacht durch {ctx.author} | Du kannst diese Nachricht erst nach dem Cooldown wiedersehen.'))
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
                    await asyncio.sleep(5)
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
                    await asyncio.sleep(5)
                    Else_check.remove(ctx.author.id)
                    return

    except Exception as err:
        return await ctx.send(embed = discord.Embed(title = 'Schwerwiegender Fehler', description = f'Ein schwerwiegender Fehler ist im Error-Handler ausgetreten. Fehlercode:\n`{error, err}`', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)))

print('getcwd:      ', os.getcwd())
print('__file__:    ', __file__)

bot.run(os.environ['DISCORD_BOT_TOKEN'])
