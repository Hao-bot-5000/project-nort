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
    async def roll(self, ctx, *args):
        num_params = len(args)

        try:
            if num_params == 0:
                value = 100
            elif num_params == 1:
                value = int(args[0])
            else:
                await ctx.send("Too many arguments")
                return
        except ValueError:
            await ctx.send("Please provide a valid number")
            return
        
        if value < 1:
            await ctx.send("The value must be greater than 0")

        roll = randint(1, value)
        reply = f"{get_emoji(':game_die:')} You rolled **{roll}** out of **{value}**!"

        await ctx.send(reply)
    
def setup(bot):
    bot.add_cog(RngCommands(bot)) 