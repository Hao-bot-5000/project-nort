import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from random             import randint
from utils              import get_emoji

class UtilCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Utility")
    
    ### Help Command ###
    @commands.command(
        brief="Displays commands",
        description="Displays all available commands offered by this bot"
    )
    @commands.guild_only()
    async def help(self, ctx, command=None, *args):
        if len(args) > 0:
            await ctx.send("Too many arguments")
            return

        if command is None:
            reply = f"{ctx.author.mention}\n"

            for cog in self.bot.cogs.values():
                reply += f"\n**{cog.category}**:"
                reply += self.__command_list_to_string(cog.get_commands())

            reply += (
                f"\n\nRun `{self.bot.command_prefix}help <command>` " + 
                "for more information on a command" + 

                f"\nYou can also run `{self.bot.command_prefix}help <category>` " + 
                "for more information on a category" 
            )
        else:
            res = await self.__get_command_or_cog(ctx, command)

            if res is None:
                return

            if isinstance(res, commands.Command):
                reply = f"{ctx.author.mention}\n\n`{self.bot.command_prefix}{res.name}"

                for param in list(res.clean_params.keys())[:-1]:
                    reply += f" <{param}>"

                reply += f"`: {res.description}"
            else:
                reply = f"{ctx.author.mention}\n\n**{res.category}**:"
                reply += self.__command_list_to_string(res.get_commands())

        await ctx.send(reply)

    ### Poll Command ###
    @commands.command(
        brief="Generates poll", 
        description="Generates a reaction-based poll based around the given message"
    )
    @commands.guild_only()
    # NOTE: unused 'args' variable acts as filler so that the 
    #       'help' command does not cut off the 'message' variable
    async def poll(self, ctx, *, message=None, args=None):
        if args is not None: # NOTE: this should never happen
            await ctx.send("This should have been impossible?!?!!")
            return

        if message is None:
            sample_member = ctx.guild.owner.display_name
            await ctx.send(
                f"Please input a message to vote on — for example: " + 
                f"`{self.bot.command_prefix}poll Is {sample_member} a real one?`"
            )
            return
        
        reply = f"Poll by **{ctx.author.display_name}**:\n\t`{message}`"

        message = await ctx.send(reply)
        await message.add_reaction(get_emoji(":thumbs_up:"))
        await message.add_reaction(get_emoji(":thumbs_down:"))

    ### Random Number Generator Command ###
    @commands.command(
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



    ### Private methods ###
    async def __get_command_or_cog(self, ctx, name):
        cmd = self.bot.get_command(name)
        if cmd is None:
            cog = next((c for c in self.bot.cogs.values() if c.category == name), None)
            if cog is None:
                await ctx.send(
                    f"No command or category called '{name}' found; run " + 
                    f"`{self.bot.command_prefix}help` for the list of all " + 
                    "available commands and categories"
                )
                return None
            
            return cog

        return cmd
    
    def __command_list_to_string(self, cmds):
        return "".join([f"\n\t`{self.bot.command_prefix}{cmd.name}`: {cmd.brief}" 
                        for cmd in cmds])

def setup(bot):
    bot.add_cog(UtilCog(bot)) 