from discord.ext import commands

class TooManyArgumentsError(commands.CommandError):
    def __init__(self, command, *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

class MemberNotFoundError(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# For throwing errors that have unique response messages
class CustomCommandError(commands.CommandError):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)
