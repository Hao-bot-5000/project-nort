import discord
from discord.ext        import commands

from cogs.base_command  import BaseCommand

from random             import randint
from utils              import get_emoji

class RngCommands(BaseCommand):
    def __init__(self, bot):
        super().__init__(bot)
    
    @commands.command(
        name="roll", 
        brief="Generates random number", 
        description="Generates a random number between 1 and the given number"
    )
    @commands.guild_only()
    async def roll(self, ctx, value=None, *args):
        if len(args) > 0:
            await ctx.send("Too many arguments")
            return

        if value is None:
            value = 100
        else:
            try:
                value = int(value)
                if value < 1:
                    await ctx.send("The value must be greater than 0")
                    return
            except ValueError:
                await ctx.send("Please provide a valid number")
                return

        roll = randint(1, value)
        reply = f"{get_emoji(':game_die:')} You rolled **{roll}** out of **{value}**!"

        await ctx.send(reply)
    
def setup(bot):
    bot.add_cog(RngCommands(bot)) 