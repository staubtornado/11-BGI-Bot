from configparser import ConfigParser
from datetime import datetime
from json import load, dump

from discord import Bot, Interaction, ButtonStyle, slash_command, ApplicationContext, Embed, User, Forbidden
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.ui import View, Button, button as ui_button

config = ConfigParser()
config.read("settings.cfg")

bd_list: list = []
user_list: list = []


async def update_lists(bot: Bot):
    now = datetime.now()
    file = get_all_data()

    bd_list.clear()
    user_list.clear()

    for entry in file:
        bd = datetime(int(file[entry][2]), int(file[entry][1]), int(file[entry][0]))
        delta: int = calculate_dates(bd, now)
        bd_list.append(delta)
        bd_list.sort()
        user: User = await bot.fetch_user(int(entry))
        user_list.insert(bd_list.index(delta), user)


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


async def edit_geburtstag(user_id: int, geburtstag: str, bot: Bot):
    date: list = geburtstag.split(".")

    with open("geburtstage.json", 'r') as f:
        file = load(f)

    file[str(user_id)] = date

    with open("geburtstage.json", "w") as f:
        dump(file, f)

    await update_lists(bot)
    return


def calculate_dates(original_date, now_date):
    delta1 = datetime(now_date.year, original_date.month, original_date.day)
    delta2 = datetime(now_date.year + 1, original_date.month, original_date.day)

    return ((delta1 if delta1 > now_date else delta2) - now_date).days


class Geburtstage(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_list_task.start()

        self.start = True

    def cog_unload(self):
        self.update_list_task.cancel()

    @tasks.loop(hours=24)
    async def update_list_task(self):
        await update_lists(self.bot)

        if not self.start:
            users: list = self.bot.get_guild(795588352387579914).members
            for i, days in enumerate(bd_list):
                bd_user: User = user_list[i]

                if days == 2:
                    for user in users:
                        if user == bd_user:
                            continue
                        if not user.bot:
                            try:
                                await user.send(f"🥳 {bd_user.mention} hat **in 3 Tagen Geburtstag**!")
                            except Forbidden:
                                continue
                elif days == 0:
                    for user in users:
                        if user == bd_user:
                            continue
                        if not user.bot:
                            try:
                                await user.send(f"🥳 {bd_user.mention} hat **morgen Geburtstag**!")
                            except Forbidden:
                                continue
        self.start = False

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
            timestamp: str = str(datetime(
                int(file[str(user.id)][2]), int(file[str(user.id)][1]), int(file[str(user.id)][0])).timestamp())[:-2]

            new: str = f"<t:" \
                       f"{timestamp}:D>: `{bd_list[i] + 1 if bd_list[i] != 364 else 0}` Tag*e verbleibend."
            embed.add_field(name=f'{i + 1}. {user}', value=new, inline=False)

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
            await edit_geburtstag(ctx.author.id, date, self.bot)
            return await ctx.respond("Dein **Geburtstag** wurde **hinzugefügt**.")
        await ctx.respond("Dein **Geburtstag** wurde **nicht hinzugefügt**.")


def setup(bot: Bot):
    bot.add_cog(Geburtstage(bot))
