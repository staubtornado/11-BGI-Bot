import asyncio
import configparser
import datetime
import json
import math
import random
from os import replace
from pathlib import Path
from time import daylight

import discord
from discord import colour
from discord.embeds import Embed
from discord.ext import commands
from discord.flags import alias_flag_value

config = configparser.ConfigParser()
config.read('settings.cfg')

class Spiele(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'tictactoe')
    async def function_tictactoe(self, ctx, enemy: discord.Member):
        field_0 = field_1 = field_2 = field_3 = field_4 = field_5 = field_6 = field_7 = field_8 = ':grey_question:'

        player_O = ctx.author
        player_X = enemy
        
        message = await ctx.send(embed = Embed(title = 'Tic Tac Toe', description = f'{player_O.mention} ist am Zug.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

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
                    return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat nicht innerhalb von 60 Sekunden seinen Zug getätigt. Das Spiel ist beendet.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

            else:
                if user == turn and reaction.message == message and str(reaction.emoji) in reactions:
                    reactions.remove(str(reaction.emoji))
                    await message.remove_reaction(str(reaction.emoji), turn)
                    await message.remove_reaction(str(reaction.emoji), self.bot.user)
                    
                    if turn == player_O:
                        X_OR_O = ':blue_circle:'
                    else:
                        X_OR_O = ':x:'
                    
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

                    if field_0 == field_1 == field_2 and field_0 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_3 == field_4 == field_5 and field_3 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_6 == field_7 == field_8 and field_6 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_0 == field_3 == field_6 and field_0 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_1 == field_4 == field_7 and field_1 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_2 == field_5 == field_8 and field_2 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_0 == field_4 == field_8 and field_0 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    elif field_2 == field_4 == field_6 and field_2 != ':grey_question:':
                        return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{turn.mention} hat gewonnen!', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
                    else:
                        await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'{next_player.mention} ist am Zug.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))

        else:
             return await message.edit(embed = Embed(title = 'Tic Tac Toe', description = f'Unentschieden, da keine Felder mehr verfügbar sind.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)) .add_field(name = 'Spieler :blue_circle:', value = player_O.mention, inline=True) .add_field(name = 'Spieler :x:', value = player_X.mention, inline=True) .add_field(name = 'Spielfeld', value = f'{field_0}⠀|⠀{field_1}⠀|⠀{field_2}\n-------------------\n{field_3}⠀|⠀{field_4}⠀|⠀{field_5}\n-------------------\n{field_6}⠀|⠀{field_7}⠀|⠀{field_8}', inline=False))
  
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

    @commands.command(name = 'hangman', aliases = ['galgenmännchen'])
    async def function_hangman(self, ctx):
        words = Path('words.txt').read_text()
        words = list(words.split(" "))
        searched_word = random.choice(words)
        
        print(searched_word)
        
        user_interface = await ctx.send(embed = Embed(title = 'Hangman', description = 'Nutzeroberfläche wird geladen, bitte warten...', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)))

        rest_of_letters = None
        reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
        for reaction in reactions:
            try:
                await user_interface.add_reaction(reaction)
            except discord.Forbidden:
                if rest_of_letters == None:
                    rest_of_letters = await ctx.send('⠀')
                await rest_of_letters.add_reaction(reaction)

        lives = 0
        letters_of_word = list(searched_word)
        used_letters = []

        def players__won(searched_word: str, used_letters: list):
            misses = 0
            right_guesses = 0

            for letter in used_letters:
                if letter in searched_word:
                    right_guesses += 1
                    if right_guesses >= len(searched_word):
                        return True
                else:
                    misses += 1
                    if misses >= 8:
                        return False

        def user_ui_update():
            return

        while lives < 8:
            if players__won(searched_word, used_letters):
                return await ctx.send(f'Sie haben gewonnen, das Wort war {searched_word}')
            else:

                def check(reaction, user):
                    if (reaction.message == user_interface or reaction.message == rest_of_letters) and str(reaction.emoji) in reactions:
                        return ((reaction.message == user_interface or reaction.message == rest_of_letters) and str(reaction.emoji) in reactions and user != self.bot.user)

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                
                except asyncio.TimeoutError:
                        return# await user_interface.edit(embed = Embed(title = 'Hangman', description = f'Man hat nicht innerhalb von 60 Sekunden seinen Zug getätigt. Das Spiel ist beendet.', colour = int(config.get('COLOUR_SETTINGS', 'standart'), base = 16)))

                else:
                    if ((reaction.message == user_interface or reaction.message == rest_of_letters) and str(reaction.emoji) in reactions and user != self.bot.user):
                    
                        if reaction.message == user_interface:
                            await user_interface.remove_reaction(str(reaction.emoji), user)
                            await user_interface.remove_reaction(str(reaction.emoji), self.bot.user)
                        if reaction.message == rest_of_letters:
                            await rest_of_letters.remove_reaction(str(reaction.emoji), user)
                            await rest_of_letters.remove_reaction(str(reaction.emoji), self.bot.user)

                        clicked_letter = None

                        if str(reaction.emoji) == '🇦':
                            clicked_letter = 'A'
                        elif str(reaction.emoji) == '🇧':
                            clicked_letter = 'B'
                        elif str(reaction.emoji) == '🇨':
                            clicked_letter = 'C'
                        elif str(reaction.emoji) == '🇩':
                            clicked_letter = 'D'
                        elif str(reaction.emoji) == '🇪':
                            clicked_letter = 'E'
                        elif str(reaction.emoji) == '🇫':
                            clicked_letter = 'F'
                        elif str(reaction.emoji) == '🇬':
                            clicked_letter = 'G'
                        elif str(reaction.emoji) == '🇭':
                            clicked_letter = 'H'
                        elif str(reaction.emoji) == '🇮':
                            clicked_letter = 'I'
                        elif str(reaction.emoji) == '🇯':
                            clicked_letter = 'J'
                        elif str(reaction.emoji) == '🇰':
                            clicked_letter = 'K'
                        elif str(reaction.emoji) == '🇱':
                            clicked_letter = 'L'
                        elif str(reaction.emoji) == '🇲':
                            clicked_letter = 'M'
                        elif str(reaction.emoji) == '🇳':
                            clicked_letter = 'N'
                        elif str(reaction.emoji) == '🇴':
                            clicked_letter = 'O'
                        elif str(reaction.emoji) == '🇵':
                            clicked_letter = 'P'
                        elif str(reaction.emoji) == '🇶':
                            clicked_letter = 'Q'
                        elif str(reaction.emoji) == '🇷':
                            clicked_letter = 'R'
                        elif str(reaction.emoji) == '🇸':
                            clicked_letter = 'S'
                        elif str(reaction.emoji) == '🇹':
                            clicked_letter = 'T'
                        elif str(reaction.emoji) == '🇺':
                            clicked_letter = 'U'
                        elif str(reaction.emoji) == '🇻':
                            clicked_letter = 'V'
                        elif str(reaction.emoji) == '🇼':
                            clicked_letter = 'W'
                        elif str(reaction.emoji) == '🇽':
                            clicked_letter = 'X'
                        elif str(reaction.emoji) == '🇾':
                            clicked_letter = 'Y'
                        elif str(reaction.emoji) == '🇿':
                            clicked_letter = 'Z'
                        
                        used_letters.append(clicked_letter)
                        await ctx.send(clicked_letter)

        await ctx.send(searched_word)


def setup(bot):
    bot.add_cog(Spiele(bot))
