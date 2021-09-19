from commands.base_command  import BaseCommand

# This, in addition to tweaking __all__ on commands/__init__.py, 
# imports all classes inside the commands package.
from commands               import *

import settings

# Register all available commands
COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}

###############################################################################


async def handle_command(command, args, message, bot_client):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix 
    # with some other bot)
    if command not in COMMAND_HANDLERS:
        await message.channel.send(
            f"That command does not exist. For more information, please run " +
            f"`{settings.COMMAND_PREFIX}commands`"
        )
        return

    # Retrieve the command
    cmd_obj = COMMAND_HANDLERS[command]

    # Check if command is through DMs and whether command can be run
    # outside of a guild
    if not message.guild and cmd_obj.guild_only:
        return

    # Print message into console
    print(
        f"{message.author.name}: {settings.COMMAND_PREFIX}{command} " + 
        " ".join(args)
    )

    # Run command
    await cmd_obj.handle(args, message, bot_client)
