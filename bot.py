import sys

import settings
import discord
from discord.ext                    import commands

from cogs                           import *
from cogs.base_command              import BaseCommand

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from multiprocessing                import Process

from utils                          import JSON_DATA_PATH, get_json_data, set_json_data

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
# TODO: dynamically store all cog files in a list
COGS = ["cogs.rng_commands", "cogs.util_commands", "cogs.yashcoin_commands"]

###############################################################################

def main():
    # Initialize the bot
    print("Starting up...")
    bot = commands.Bot(intents=intents, command_prefix=settings.COMMAND_PREFIX)

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
        else:
            raise error

    async def handle_guilds(guild, is_joining):
        json_data = await get_json_data(JSON_DATA_PATH)
        
        if is_joining:
            json_data[guild.id] = {}
        else:
            json_data.pop(guild.id, None)

        await set_json_data(JSON_DATA_PATH, json_data)

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
