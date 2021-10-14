from discord.ext import commands

class TooManyArgumentsError(commands.CommandError):
    def __init__(self, command, *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

class MemberNotFoundError(commands.CommandError):
    def __init__(self, member, *args, **kwargs):
        self.member = member
        super().__init__(*args, **kwargs)

class InvalidTypeError(commands.CommandError):
    def __init__(self, type, *args, **kwargs):
        self.type = type
        super().__init__(*args, **kwargs)
