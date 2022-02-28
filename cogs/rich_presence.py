from discord import ActivityType, Activity
from discord.ext import tasks
from discord.ext.commands import Cog


class rich_presence(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rich_presence_update.start()

    def cog_unload(self):
        self.rich_presence_update.cancel()

    @tasks.loop(seconds=20)
    async def rich_presence_update(self):
        # ferien = datetime.datetime(2021, 12, 23, 10, 15)
        # heute = datetime.datetime.today().replace(microsecond=0)

        await self.bot.wait_until_ready()
        await self.bot.change_presence(activity=Activity(type=ActivityType.listening,
                                                         name=f"Python 3.9"))


def setup(bot):
    bot.add_cog(rich_presence(bot))
