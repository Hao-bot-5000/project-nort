import discord
from discord.ext        import commands

from cogs.base_command  import BaseCommand
class UtilCommands(BaseCommand):
    def __init__(self, bot):
        super().__init__(bot)
    
    @commands.command(
        name="commands", 
        brief="Displays commands",
        description="Displays all available commands offered by this bot"
    )
    @commands.guild_only()
    async def cmds(self, ctx):
        msg = f"{ctx.author.mention}\n"

        await ctx.send(msg, "WIP -- use the default `!nort help` for now")
    
def setup(bot):
    bot.add_cog(UtilCommands(bot)) 