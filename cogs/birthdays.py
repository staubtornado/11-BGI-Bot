from configparser import ConfigParser
from datetime import datetime
from json import load, dump

from discord import Bot, Interaction, ButtonStyle, slash_command, ApplicationContext, Embed
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.ui import View, Button, button as ui_button

config = ConfigParser()
config.read("settings.cfg")

bd_list: list = []
user_list: list = []


def update_lists():
    now = datetime.now()
    file = get_all_data()

    bd_list.clear()
    user_list.clear()

    for entry in file:
        bd = datetime(int(file[entry][2]), int(file[entry][1]), int(file[entry][0]))
        delta: int = calculate_dates(bd, now)
        bd_list.append(delta)
        bd_list.sort()
        user_list.insert(bd_list.index(delta), entry)


class ConfirmButton(View):
    def __init__(self):
        super().__init__()
        self.value = None

    @ui_button(
        label="Ja",
        style=ButtonStyle.green,
        custom_id='56345634',
    )
    async def accept(self, button: Button, interaction: Interaction):
        self.value = True
        self.stop()

    @ui_button(
        label="Nein",
        style=ButtonStyle.red,
        custom_id='67547564',
    )
    async def decline(self, button: Button, interaction: Interaction):
        self.value = False
        self.stop()


def get_all_data():
    with open("geburtstage.json", 'r') as f:
        file = load(f)
    return file


def edit_geburtstag(user_id: int, geburtstag: str):
    date: list = geburtstag.split(".")

    with open("geburtstage.json", 'r') as f:
        file = load(f)

    file[str(user_id)] = date

    with open("geburtstage.json", "w") as f:
        dump(file, f)

    update_lists()
    return


def calculate_dates(original_date, now_date):
    delta1 = datetime(now_date.year, original_date.month, original_date.day)
    delta2 = datetime(now_date.year + 1, original_date.month, original_date.day)

    return ((delta1 if delta1 > now_date else delta2) - now_date).days


class Geburtstage(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_list_task.start()

    def cog_unload(self):
        self.update_list_task.cancel()

    @tasks.loop(hours=1)
    async def update_list_task(self):
        update_lists()

    @slash_command()
    async def geburtstage(self, ctx: ApplicationContext):
        """Zeigt die nächsten 25 Geburtstage auf diesem Sever an."""
        await ctx.defer()
        file = get_all_data()

        embed = Embed(title='Geburtstage',
                      description=f'Geburtstage auf diesem Server.\nNutze **/**`add_birthday DD.MM.YYYY` um '
                                  f'deinen Geburtstag hinzuzufügen.',
                      colour=int(config.get('COLOUR_SETTINGS', 'standard'), base=16))

        for i, user in enumerate(user_list):
            new: str = f"<t:" \
                       f"{str(datetime(int(file[user][2]), int(file[user][1]), int(file[user][0])).timestamp())[:-2]}" \
                       f":D>: `{bd_list[i]}` Tag*e verbleibend."

            d_user = await self.bot.fetch_user(int(user))
            embed.add_field(name=f'{i + 1}. {d_user}', value=new, inline=False)

            if i >= 24:
                break
        return await ctx.respond(embed=embed)

    @slash_command()
    async def add_birthday(self, ctx: ApplicationContext, date: str):
        """Fügt das gegebene Datum zum Kalender hinzu. Für alle Nutzer auf diesem Server sichtbar."""
        await ctx.defer()
        view = ConfirmButton()
        await ctx.respond("Dein Geburtstag entspricht dem `DD.MM.YYYY`-Format?", view=view)

        await view.wait()
        if view.value is None:
            return
        if view.value:
            edit_geburtstag(ctx.author.id, date)
            return await ctx.respond("Dein **Geburtstag** wurde **hinzugefügt**.")
        await ctx.respond("Dein **Geburtstag** wurde **nicht hinzugefügt**.")


def setup(bot: Bot):
    bot.add_cog(Geburtstage(bot))
