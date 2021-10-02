import os
import sys

from discord.ext.commands.errors import ArgumentParsingError

import settings
import discord
from discord.ext                    import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from multiprocessing                import Process

from utils                          import (get_json_path, get_json_data, set_json_data,
                                            get_emoji)
import custom_errors

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

###############################################################################

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

    @bot.before_invoke
    async def print_command_in_console(ctx):
        print(f"{ctx.author.name}: {ctx.message.content}")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"That command does not exist. For more information, please run " +
                f"`{bot.command_prefix}help`"
            )
        elif isinstance(error, custom_errors.TooManyArgumentsError):
            await ctx.send(
                "You have entered too many arguments. Please run " +
                f"`{bot.command_prefix}help {error.command}` for more information " +
                "on this command"
            )
        elif isinstance(error, custom_errors.MemberNotFoundError):
            await ctx.send(
                f"You are not a member of YashCoin{get_emoji(':tm:')} Incorporated"
            )
        elif isinstance(error, custom_errors.CustomCommandError):
            await ctx.send(error.message)
        elif isinstance(error, ArgumentParsingError):
            await ctx.send(
                f"You have entered an improper argument. Please make sure that " +
                "your arguments are properly formatted"
            )
            print(error) # in case it isn't just an issue with improper quotation marks
        else:
            raise error

    async def handle_guilds(guild, is_joining):
        path = get_json_path("data")
        json_data = await get_json_data(path)

        if is_joining:
            json_data[guild.id] = {}
        else:
            json_data.pop(guild.id, None)

        await set_json_data(path, json_data)

    @bot.event
    async def on_guild_join(guild):
        await handle_guilds(guild, is_joining=True)

    @bot.event
    async def on_guild_remove(guild):
        await handle_guilds(guild, is_joining=False)

    # Finally, set the bot running
    bot.run(settings.BOT_TOKEN)

###############################################################################


if __name__ == "__main__":
    main()
