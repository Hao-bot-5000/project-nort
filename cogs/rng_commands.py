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
        description="Generates a random number between two given numbers"
    )
    @commands.guild_only()
    async def roll(self, ctx, *args):
        num_params = len(args)

        try:
            if num_params == 0:
                lower = 1
                upper = 100
            elif num_params == 1:
                lower = 1
                upper = int(args[0])
            elif num_params == 2:
                lower = int(args[0])
                upper = int(args[1])
            else:
                await ctx.send("Too many arguments")
                return
        except ValueError:
            await ctx.send("Please provide valid numbers")
            return
        
        if lower < 1:
            await ctx.send("The values must be greater than 0")

        if lower > upper:
            await ctx.send("The lower bound cannot be higher than the upper bound")
            return

        value = randint(lower, upper)
        reply = f"{get_emoji(':game_die:')} You rolled **{value}** out of **{upper}**!"

        await ctx.send(reply)
    
def setup(bot):
    bot.add_cog(RngCommands(bot)) 