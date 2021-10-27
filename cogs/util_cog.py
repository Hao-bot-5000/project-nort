import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from random             import randint
from utils              import get_emoji
from custom_errors      import TooManyArgumentsError

class UtilCog(BaseCog, name="Utility"):
    def __init__(self, bot):
        super().__init__(bot)

    ### Help Command ###
    @commands.command(
        brief="Displays commands",
        description="Displays all available commands offered by this bot"
    )
    @commands.guild_only()
    async def help(self, ctx, command=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("help")

        try:
            await ctx.send(self.create_help_message(ctx.author, command))
        except ValueError:
            await ctx.send(
                f"No command or category called '{command}' found; run " +
                f"`{self.bot.command_prefix}help` for the list of all " +
                "available commands and categories"
            )

    ### Poll Command ###
    @commands.command(
        brief="Generates poll",
        description="Generates a poll that members can participate in "
                    "by reacting to the given options (maximum of 10)"
    )
    @commands.guild_only()
    # NOTE: unused variable at the end acts as filler so that the
    #       'help' command does not cut off the 'options' variable
    async def poll(self, ctx, message=None, *options, _=None):
        num_options = len(options)

        if num_options > len(self.POLL_EMOJIS):
            raise TooManyArgumentsError("poll")

        if message is None:
            await ctx.send(self.create_sample_poll_message(ctx.guild.owner.display_name))
            return

        embed_reply = self.create_embed()
        embed_reply.set_author(
            name=f"Poll by {ctx.author.display_name}:",
            icon_url=ctx.author.avatar_url
        )

        self.add_poll_options(embed_reply, message, options, num_options)
        await self.add_poll_reactions((await ctx.send(embed=embed_reply)), num_options)

    ### Random Number Generator Command ###
    @commands.command(
        brief="Generates random number",
        description="Generates a random number between 1 and the given number"
    )
    @commands.guild_only()
    async def roll(self, ctx, value=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("roll")

        value = self.input_to_positive_int(value, 100)
        roll = randint(1, value)

        await ctx.send(
            f"{get_emoji(':game_die:')} You rolled **{roll}** out of **{value}**!"
        )

    ### Reload Command ###
    @commands.command(
        brief="Reload commands (me only)",
        description="Reload all commands, useful for quick updates"
    )
    @commands.is_owner()
    async def reload(self, ctx):
        from bot import COGS
        for cog in COGS:
            self.bot.reload_extension(cog)
        await ctx.send("All commands successfully reloaded!")



    ### Helper Methods ###
    def create_help_message(self, author, input=None):
        """
            Return a help message based on the given input.

            Parameters
            ----------
            author: :class:`discord.Member`
                a discord member that sent the help command.
            input: :class:`str, optional`
                the name of a command or cog.
            
            Returns
            -------
            reply: :class:`str`
                a help message for the given discord member.

            Raises
            ------
            ValueError:
                a command or cog could not be found from ``input``.
        """

        mention = f"{author.mention}\n"

        if input is None:
            return mention + (
                "\n".join(f"**{c.qualified_name}**: {self.cog_get_commands_as_str(c)}"
                          for c in self.bot.cogs.values()) +

                f"\n\nRun `{self.bot.command_prefix}help <command>` " +
                "for more information on a command" +

                f"\nYou can also run `{self.bot.command_prefix}help <category>` " +
                "for more information on a category"
            )

        command = self.bot.get_command(input)
        if command is not None:
            return mention + (
                f"\n`{self.bot.command_prefix}{command.name}" +
                "".join(f" <{p}>" for p in list(command.clean_params.keys())[:-1]) +
                f"`: {command.description}" +

                (f"\n\nAliases: `{', '.join(a for a in command.aliases)}`"
                 if len(command.aliases) > 0 else "")
            )

        cog = self.bot.get_cog(input)
        if cog is not None:
            return mention + (
                f"\n**{cog.qualified_name}**:{self.cog_get_commands_as_str(cog)}"
            )

        raise ValueError(f"Could not find a command or cog called '{input}'")

    def cog_get_commands_as_str(self, cog):
        """
            Return a string that lists out all the commands of a given cog.

            Parameters
            ----------
            cog: :class:`discord.Cog`
                a cog that has been loaded onto the bot.

            Returns
            -------
            commands: :class:`str`
                a string representation of every command defined inside ``cog``.
        """

        return "".join(f"\n\t`{self.bot.command_prefix}{command.name}`: {command.brief}"
                       for command in cog.get_commands())

    def create_sample_poll_message(self, sample_name):
        """
            Return a message that displays how the poll command works.

            Parameters
            ----------
            sample_name: :class:`str`
                an input to use as part of the sample message.

            Returns
            -------
            sample_message: :class:`str`
                an example message for the poll command.
        """

        return (
            f"Please input a message to vote on — for example: " +
            f"`{self.bot.command_prefix}poll \"Is {sample_name} a real one?\" Yes No`"
        )

    # Poll Reaction Helper Methods #
    DEFAULT_EMOJIS = (get_emoji(":thumbs_up:"), get_emoji(":thumbs_down:"))
    POLL_EMOJIS = (get_emoji(":one:"),   get_emoji(":two:"),   get_emoji(":three:"),
                   get_emoji(":four:"),  get_emoji(":five:"),  get_emoji(":six:"),
                   get_emoji(":seven:"), get_emoji(":eight:"), get_emoji(":nine:"),
                   get_emoji(":ten:"))

    def add_poll_options(self, embed, message, options=(), num_options=0):
        """
            Add to the embed the given poll message and options. If the number of options
            given is ``0``, the default ``("Yes", "No")`` options will be added.

            Parameters
            ----------
            embed: :class:`discord.Embed`
                an embed to display the poll options on.
            message: :class:`str`
                a poll message.
            options: :class:`tuple[str]`
                the poll options.
            num_options: :class:`int`
                the number of poll options.
        """

        if num_options == 0:
            options = ("Yes", "No")
            emojis = self.DEFAULT_EMOJIS
        else:
            emojis = self.POLL_EMOJIS[:num_options]

        embed.add_field(
            name=f"**{message}**",
            value='\n'.join(f"{e} `{o}`" for e, o in zip(emojis, options))
        )

    async def add_poll_reactions(self, message, num_options=0):
        """
            React to a message with the given amount of poll options. If the number of
            options given is ``0``, the default thumbs up/down reactions will be used.

            Parameters
            ----------
            message: :class:`discord.Message`
                a discord message.
            num_options: :class:`int`
                the number of reactions to create.
        """

        if num_options == 0:
            await self.add_reactions(message, *self.DEFAULT_EMOJIS)
            return

        await self.add_reactions(message, *self.POLL_EMOJIS[:num_options])


def setup(bot):
    bot.add_cog(UtilCog(bot))