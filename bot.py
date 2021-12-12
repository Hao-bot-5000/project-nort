import os
import sys
import traceback
from multiprocessing                import Process

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext                    import commands

import settings
from utils                          import get_json_data, get_json_path, set_json_data

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()

# Setting up intents
intents = discord.Intents.default()
intents.members = True

# Register all available cogs
COGS = [f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs")
        if filename.endswith(".py") and filename != "base_cog.py"]

#########################################################################################

def main():
    # Initialize the bot
    print("Starting up...")
    bot = commands.Bot(intents=intents, command_prefix=settings.COMMAND_PREFIX,
                       help_command=None)

    # Load up all available cogs
    print(f"List of cogs: {COGS}")
    for cog in COGS:
        bot.load_extension(cog)

    # Define event handlers for the bot
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running flag
    @bot.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if settings.NOW_PLAYING:
            print("Setting NP game", flush=True)
            await bot.change_presence(
                  activity=discord.Game(name=settings.NOW_PLAYING))
        print("Logged in!", flush=True)

    # NOTE: This event seems to not get triggered if an error is caught (by discord.py)
    # before the command function is even invoked.
    @bot.before_invoke
    async def print_command_in_console(ctx):
        print(f"{ctx.author.name}: {ctx.message.content}")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                "That command does not exist. For more information, please run " +
                f"`{bot.command_prefix}help`"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You have not entered enough arguments. Please run " +
                f"`{bot.command_prefix}help {ctx.command}` " +
                "for more information on this command"
            )
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                "You have entered too many arguments. Please run " +
                f"`{bot.command_prefix}help {ctx.command}` " +
                "for more information on this command"
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"Member {error.argument} could not be found in this server")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                "You have entered an invalid argument. Please make sure that your " +
                "argument is a valid input for this command"
            )
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(
                "You have entered an improper argument. Please make sure that " +
                "your arguments are properly formatted"
            )
        else:
            await ctx.send("Something went wrong...")
            traceback.print_exception(type(error), error, error.__traceback__)

    async def handle_guilds(guild, is_joining):
        path = get_json_path("data")
        json_data = get_json_data(path)

        if is_joining:
            json_data[guild.id] = {}
        else:
            json_data.pop(guild.id, None)

        set_json_data(path, json_data)

    @bot.event
    async def on_guild_join(guild):
        await handle_guilds(guild, is_joining=True)

    @bot.event
    async def on_guild_remove(guild):
        await handle_guilds(guild, is_joining=False)

    # Finally, set the bot running
    bot.run(settings.BOT_TOKEN)

#########################################################################################


if __name__ == "__main__":
    main()
