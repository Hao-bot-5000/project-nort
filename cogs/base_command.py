from discord.ext        import commands

class BaseCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
