import configparser
import datetime

import discord
from discord import Embed
from discord.ext import commands
from discord.commands import SlashCommandGroup
import json

config = configparser.ConfigParser()
config.read('settings.cfg')


class ConfirmButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Ja",
        style=discord.ButtonStyle.green,
        custom_id='56345634',
    )
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(
        label="Nein",
        style=discord.ButtonStyle.red,
        custom_id='67547564',
    )
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()


def get_all_data():
    with open("geburtstage.json", 'r') as f:
        file = json.load(f)
    return file


def get_geburtstag(user_id: int):
    with open("geburtstage.json", 'r') as f:
        file = json.load(f)
    return file[str(user_id)]


def edit_geburtstag(user_id: int, geburtstag: str):
    date: list = geburtstag.split(".")

    with open("geburtstage.json", 'r') as f:
        file = json.load(f)

    file[str(user_id)] = date

    with open("geburtstage.json", "w") as f:
        json.dump(file, f)
    return


def get_user_birthday(year: int, month: int, day: int):
    birthday = datetime.datetime(year, month, day)
    return birthday


def calculate_dates(original_date, now_date):
    delta1 = datetime.datetime(now_date.year, original_date.month, original_date.day)
    delta2 = datetime.datetime(now_date.year + 1, original_date.month, original_date.day)

    return ((delta1 if delta1 > now_date else delta2) - now_date).days


birthday_kalndr: SlashCommandGroup = SlashCommandGroup("birthday", "Befehle der Geburtstage")


class GeburtstagsKalender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @birthday_kalndr.command(name="geburtstage", guild_ids=[795588352387579914])
    async def geburtstage(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            message = await ctx.send(
                embed=Embed(title="Geburtstage", description="<a:loading:820216894703009842> Kalender wird "
                                                             "geladen, bitte warten...")
                    .set_footer(text="Diese Liste an Geburtstagen ist sau ineffizient geschrieben und wird "
                                     "jedes mal neu berechnet."))

            now = datetime.datetime.now()
            file = get_all_data()

            temp_bd_list: list = []
            user_list: list = []

            for entry in file:
                bd = get_user_birthday(int(file[entry][2]), int(file[entry][1]), int(file[entry][0]))
                temp_bd_list.append(calculate_dates(bd, now))
                temp_bd_list.sort()
                index = temp_bd_list.index(calculate_dates(bd, now))
                user_list.insert(index, entry)
            del temp_bd_list

            embed = Embed(title='Geburtstage',
                          description=f'Geburtstage auf diesem Server.\nNutze `/geburtstage add (geburtsdatum)` um '
                                      f'deinen Geburtstag hinzuzufügen.', colour=int(
                    config.get('COLOUR_SETTINGS', 'standard'), base=16))

            counter: int = 0
            for user in user_list:
                counter += 1
                bd = get_user_birthday(int(file[user][2]), int(file[user][1]), int(file[user][0]))

                d_user = await self.bot.fetch_user(int(user))
                embed.add_field(name=f'{counter}. {d_user}', value=str(bd)[:-9],
                                inline=False)

                if counter >= 25:
                    break
            return await message.edit(embed=embed)

    @birthday_kalndr.command(name="geburtstage", guild_ids=[795588352387579914])
    async def add(self, ctx, date: str):
        view = ConfirmButton()
        await ctx.send("Dein Geburtstag entspricht dem `DD.MM.YYYY`-Format?", view=view)

        await view.wait()
        if view.value is None:
            return
        elif view.value:
            edit_geburtstag(ctx.author.id, date)
            return await ctx.send("Dein Geburtstag wurde hinzugefügt.")
        else:
            return await ctx.send("Dein Geburtstag wurde **nicht** hinzugefügt.")


def setup(bot):
    bot.add_cog(GeburtstagsKalender(bot))
