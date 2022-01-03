import asyncio
import configparser
import json
import random

import discord
from discord import Embed
from discord.ext import commands

config = configparser.ConfigParser()
config.read('settings.cfg')

multiplikator = float(config.get('BOT_SETTINGS', 'level_increase'))


def get_data(user, data_type):
    with open("levels.json", 'r') as f:
        file = json.load(f)
        return file[str(user.id)][data_type]


async def xp_to_level(user: discord.member, level, xp):
    if xp >= round((250 * multiplikator ** level)):
        with open("levels.json", "r") as f:
            file = json.load(f)
        file[str(user.id)][0] += 1
        file[str(user.id)][1] -= round((250 * multiplikator ** level))

        with open("levels.json", "w") as f:
            json.dump(file, f)
        return True
    else:
        return False


async def edit_data(user: discord.member, data_type, amount):
    with open("levels.json", "r") as f:
        file = json.load(f)

    try:
        file[str(user.id)]
    except KeyError:
        file[str(user.id)] = [0, 0, 0]

    file[str(user.id)][data_type] += amount

    with open("levels.json", "w") as f:
        json.dump(file, f)
    return


users_that_have_to_wait = []


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.content.startswith(config.get('BOT_SETTINGS', 'prefix'), 0,
                                                            1) or message.guild is None:
            return
        await(edit_data(message.author, 2, 1))

        if message.author.id in users_that_have_to_wait:
            return
        else:
            await(edit_data(message.author, 1, random.randint(15, 25)))
            users_that_have_to_wait.append(message.author.id)
            if await(xp_to_level(message.author, get_data(message.author, 0), get_data(message.author, 1))):
                await message.channel.send(embed=Embed(title='Levelaufstieg', description='Du bist ein Level '
                                                                                          'aufgestiegen. Weiter '
                                                                                          'so!', colour=int(
                    config.get('COLOUR_SETTINGS', 'standard'), base=16))
                                           .add_field(name='Level', value=get_data(message.author, 0))
                                           .add_field(name='XP für nächstes Level',
                                                      value=round((250 * multiplikator ** get_data(message.author, 0))))
                                           .add_field(name='Gesendete Nachrichten', value=get_data(message.author, 2))
                                           .set_author(name=message.author, icon_url=message.author.avatar.url),
                                           delete_after=60)
            await asyncio.sleep(60)
            users_that_have_to_wait.remove(message.author.id)
            return

    @commands.command(name="rank", aliases=['level'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rank(self, ctx, *, selected_user: discord.Member = None):
        if selected_user is None:
            target: discord.Member = ctx.author
        else:
            target = selected_user

        try:
            white_square = '◻️'
            black_square = '▪️'

            percent = (get_data(target, 1) / (250 * multiplikator ** get_data(target, 0)) * 100)
            bar = round(percent / 10) * white_square + round((100 - percent) / 10) * black_square

            return await ctx.send(
                embed=Embed(title='Statistik', colour=int(
                    config.get('COLOUR_SETTINGS', 'standard'), base=16))
                    .add_field(name='Level', value=get_data(target, 0))
                    .add_field(name='XP',
                               value=f'{get_data(target, 1)} / {round((250 * multiplikator ** get_data(target, 0)))}')
                    .add_field(name='Nachrichten', value=get_data(target, 2))
                    .add_field(name='Fortschritt', value=bar)
                    .set_author(name=target, icon_url=target.avatar.url))
        except KeyError:
            return await ctx.send(embed=Embed(title='Fehler', description='Irgendwas ist schief gelaufen. '
                                                                          'Anscheinend haben wir noch keine '
                                                                          'Informationen über diesen Nutzer.',
                                              colour=int(config.get('COLOUR_SETTINGS', 'error'), base=16)).set_author(
                name=target, icon_url=target.avatar.url))

    @commands.command(name='levels', aliases=['leaderboard', 'ranks'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def levels(self, ctx):
        with open("levels.json", 'r') as f:
            file = json.load(f)

        user_list = {}

        for user in file:
            temp_user_level = file[user][0] + (file[user][1] / (250 * multiplikator ** file[user][0]))
            user_list[user] = temp_user_level

        user_list = list(reversed(dict(sorted(user_list.items(), key=lambda item: item[1]))))

        embed = Embed(title='Leaderboard', description='Top-Level auf diesem Server. Nutze `/rank @user` um weitere '
                                                       'Informationen über einen Nutzer zu erhalten.', colour=int(
            config.get('COLOUR_SETTINGS', 'standard'), base=16))

        counter = 0
        for entry in user_list:
            counter += 1

            user = await self.bot.fetch_user(int(entry))
            embed.add_field(name=f'{counter}. {user}', value=f'{file[entry][0]}L | {file[entry][1]}XP',
                            inline=False)

            if counter >= 25:
                break
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leveling(bot))
