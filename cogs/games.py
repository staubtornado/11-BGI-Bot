from time import daylight
import discord
from discord import colour
from discord.embeds import Embed
from discord.ext import commands
import configparser
import asyncio
import json
import datetime
import math

from discord.flags import alias_flag_value

config = configparser.ConfigParser()
config.read('settings.cfg')

class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'tictactoe')
    async def function_tictactoe(self, ctx, enemy: discord.Member):
        field_0 = field_1 = field_2 = field_3 = field_4 = field_5 = field_6 = field_7 = field_8 = None

        player_O = ctx.author
        player_X = enemy
        
        message = await ctx.send(embed = Embed(title = 'Tic Tac Toe', description = f'{player_O.mention} ist am Zug.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        for reaction in reactions:
            await message.add_reaction(reaction)
        
        for i in range(9):
            if i % 2 == 0:
                turn = player_O
                next_player = player_X
            else:
                turn = player_X
                next_player = player_O
            
            def check(reaction, user):
                if user == turn and reaction.message == message and str(reaction.emoji) in reactions:
                    return user == turn and reaction.message == message and str(reaction.emoji) in reactions

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            
            except asyncio.TimeoutError:
                    return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat nicht innerhalb von 60 Sekunden seinen Zug getätigt. Das Spiel ist beendet.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

            else:
                if user == turn and reaction.message == message and str(reaction.emoji) in reactions:
                    reactions.remove(str(reaction.emoji))
                    await message.remove_reaction(str(reaction.emoji), turn)
                    await message.remove_reaction(str(reaction.emoji), self.bot.user)
                    
                    if turn == player_O:
                        X_OR_O = 'O'
                    else:
                        X_OR_O = 'X'
                    
                    if str(reaction.emoji) == '1️⃣':
                        field_0 = X_OR_O
                    elif str(reaction.emoji) == '2️⃣':
                        field_1 = X_OR_O
                    elif str(reaction.emoji) == '3️⃣':
                        field_2 = X_OR_O
                    elif str(reaction.emoji) == '4️⃣':
                        field_3 = X_OR_O
                    elif str(reaction.emoji) == '5️⃣':
                        field_4 = X_OR_O
                    elif str(reaction.emoji) == '6️⃣':
                        field_5 = X_OR_O
                    elif str(reaction.emoji) == '7️⃣':
                        field_6 = X_OR_O
                    elif str(reaction.emoji) == '8️⃣':
                        field_7 = X_OR_O
                    elif str(reaction.emoji) == '9️⃣':
                        field_8 = X_OR_O

                    if field_0 == field_1 == field_2 and field_0 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_3 == field_4 == field_5 and field_3 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_6 == field_7 == field_8 and field_6 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_0 == field_3 == field_6 and field_0 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_1 == field_4 == field_7 and field_1 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_2 == field_5 == field_8 and field_2 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_0 == field_4 == field_8 and field_0 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_2 == field_4 == field_6 and field_2 != None:
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    else:
                        await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{next_player.mention} ist am Zug.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

        else:
             return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'Unentschieden, da keine Felder mehr verfügbar sind.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler O', value = player_O.mention, inline=True) .add_field(name = 'Spieler X', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
  
    @commands.command(name = 'biobuch')
    async def function_biobuch(self, ctx):
        antonio = ctx.guild.get_member(404638895934930945)
        
        await ctx.send(embed = Embed(title = 'Biobuch', description = f'{antonio.mention} hat sein Biobuch nicht zurück gegeben. Er wird daran erinnert.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)))
        
        try:
            await antonio.send(embed = Embed(title = 'Biobuch', description = 'Du hast dein Biobuch nicht zurückgegeben.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)))
        except discord.Forbidden:
            return await ctx.send(embed = Embed(title = 'Fehler', description = f'{antonio.mention} will nicht daran erinnert werden.', colour = int(config.get('COLOUR_SETTINGS', 'error'), base = 16)))
        else:
            return

    @commands.group(name = 'antonio', pass_context = True)
    async def function_antonio(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("antonio.json", "r") as f:
                file = json.load(f)

            d0 = datetime.datetime(2021, 8, 30)
            d1 = datetime.datetime.now()
            delta = d1 - d0
            
            tage_gesamt = delta.days - ((math.trunc(delta.days / 7) * 2))
            verpasster_unterricht = 0
            
            alle_verspätungen = file['verspaetungen']
            for verspätung in alle_verspätungen:
                verpasster_unterricht += verspätung
            
            return await ctx.send(embed = Embed(title = 'Antonio\'s Statistiken', description = f'Statistiken über Unannehmlichkeiten unseres Antonio\'s seit {tage_gesamt} Schultag*en.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16))
                .add_field(name = 'Höchste Verspätung', value = f'{max(alle_verspätungen)} Minuten')
                .add_field(name = 'Anzahl der Verspätungen' , value = len(alle_verspätungen))
                .add_field(name = 'Verspätungen Ø', value = f'{round(verpasster_unterricht / len(alle_verspätungen), 2)} Minuten')
                .add_field(name = 'Verpasste Unterrichtszeit', value = f'{verpasster_unterricht} Minuten')
                .add_field(name = '⠀', value = '⠀', inline=False)
                .add_field(name = 'Testheft vergessen', value = file['testheft_vergessen'])
                .add_field(name = 'Hausaufgaben vergessen', value = file['hausaufgaben_vergessen'])
                ) 

    @function_antonio.command(name = 'add')
    async def function_antonio_add(ctx, verspätung: int):
        print(ctx.message.content)
        with open("antonio.json", "r") as f: 
            file = json.load(f)
        
            file['verspaetungen'].append(verspätung)

        with open("antonio.json", "w") as f:
            json.dump(file, f)
        return await ctx.message.add_reaction('✅')

    @function_antonio.command(name = 'testheft')
    async def function_antonio_add(ctx):
        with open("antonio.json", "r") as f:
            file = json.load(f)
        
            file['testheft_vergessen'] += 1

        with open("antonio.json", "w") as f:
            json.dump(file, f)
        return await ctx.message.add_reaction('✅')

def setup(bot):
    bot.add_cog(games(bot))