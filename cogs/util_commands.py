import discord
from discord.ext        import commands

from cogs.base_command  import BaseCommand
class UtilCommands(BaseCommand):
    def __init__(self, bot):
        super().__init__(bot)
    
    @commands.command(
        name="help", 
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

            cmds = list(self.bot.commands)
            cmds.sort(key=lambda cmd: cmd.name)
            for cmd in cmds:
                reply += f"\n**{self.bot.command_prefix}{cmd.name}**: {cmd.brief}"
            
            reply += (
                f"\n\nRun `{self.bot.command_prefix}help <command>` " + 
                "for more information on a command"
            )
        else:
            cmd = self.bot.get_command(command)

            if cmd is None:
                await ctx.send(
                    f"No command called '{command}' found; run " + 
                    f"`{self.bot.command_prefix}help` for the list of all " + 
                    "available commands"
                )
                return
            
            reply = f"{ctx.author.mention}\n\n**{self.bot.command_prefix}{cmd.name}**"

            for param in list(cmd.clean_params.keys())[:-1]:
                reply += f" *<{param}>*"

            reply += f": {cmd.description}"

        await ctx.send(reply)
    
def setup(bot):
    bot.add_cog(UtilCommands(bot)) 