import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from random             import randint
from utils              import get_emoji, create_black_embed
from custom_errors      import TooManyArgumentsError

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
            raise TooManyArgumentsError("help")

        reply = f"{ctx.author.mention}\n"

        if command is None:
            for cog in self.bot.cogs.values():
                reply += (
                    f"\n**{cog.category}**:" +
                    self.__command_list_to_string(cog.get_commands())
                )

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
                reply += (
                    f"\n`{self.bot.command_prefix}{res.name}" +
                    "".join(f" <{p}>" for p in list(res.clean_params.keys())[:-1]) +
                    f"`: {res.description}"
                )
                if len(res.aliases) > 0:
                    reply += f"\n\nAliases: `{', '.join(a for a in res.aliases)}`"
            else:
                reply += (
                    f"\n**{res.category}**:" +
                    self.__command_list_to_string(res.get_commands())
                )

        await ctx.send(reply)

    ### Poll Command ###
    @commands.command(
        brief="Generates poll",
        description="Generates a poll that members can participate in "
                    "by reacting to the given options (maximum of 10)"
    )
    @commands.guild_only()
    # NOTE: unused 'args' variable acts as filler so that the
    #       'help' command does not cut off the 'message' variable
    async def poll(self, ctx, message=None, *options, args=None):
        num_options = len(options)

        if num_options > 10:
            raise TooManyArgumentsError("poll")

        if message is None:
            sample_member = ctx.guild.owner.display_name
            await ctx.send(
                f"Please input a message to vote on — for example: " +
                f"`{self.bot.command_prefix}poll \"Is {sample_member} a real one?\" " +
                "yes no`"
            )
            return

        embed_reply = create_black_embed()

        embed_reply.set_author(
            name=f"Poll by {ctx.author.display_name}:",
            icon_url=ctx.author.avatar_url
        )

        self.__add_poll_options(message, embed_reply, options, num_options)
        await self.__add_poll_reactions(await ctx.send(embed=embed_reply), num_options)

    ### Random Number Generator Command ###
    @commands.command(
        brief="Generates random number",
        description="Generates a random number between 1 and the given number"
    )
    @commands.guild_only()
    async def roll(self, ctx, value=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("roll")

        try:
            value = int(value) if value is not None else 100
            if value < 1: raise ValueError()
        except ValueError:
            await ctx.send("Please provide a valid positive number")
            return

        roll = randint(1, value)
        reply = f"{get_emoji(':game_die:')} You rolled **{roll}** out of **{value}**!"

        await ctx.send(reply)

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



    ### Private methods ###
    async def __get_command_or_cog(self, ctx, name):
        cmd = self.bot.get_command(name)

        if cmd is not None:
            return cmd

        cog = next((c for c in self.bot.cogs.values() if c.category == name), None)
        if cog is None:
            await ctx.send(
                f"No command or category called '{name}' found; run " +
                f"`{self.bot.command_prefix}help` for the list of all " +
                "available commands and categories"
            )
        return cog

    def __command_list_to_string(self, cmds):
        return "".join(f"\n\t`{self.bot.command_prefix}{cmd.name}`: {cmd.brief}"
                       for cmd in cmds)

    __POLL_EMOJIS = (get_emoji(":one:"),   get_emoji(":two:"),   get_emoji(":three:"),
                     get_emoji(":four:"),  get_emoji(":five:"),  get_emoji(":six:"),
                     get_emoji(":seven:"), get_emoji(":eight:"), get_emoji(":nine:"),
                     get_emoji(":ten:"))
    def __add_poll_options(self, message, embed, options, num_options):
        if num_options == 0:
            options = ("Yes", "No")
            emojis = (get_emoji(":thumbs_up:"), get_emoji(":thumbs_down:"))
        else:
            emojis = self.__POLL_EMOJIS[:num_options]

        embed.add_field(
            name=f"**{message}**",
            value='\n'.join(f"{e} `{o}`" for e, o in zip(emojis, options)),
        )

    async def __add_poll_reactions(self, message, num_options):
        if num_options == 0:
            await message.add_reaction(get_emoji(":thumbs_up:"))
            await message.add_reaction(get_emoji(":thumbs_down:"))
            return

        for i in range(num_options):
            await message.add_reaction(self.__POLL_EMOJIS[i])

def setup(bot):
    bot.add_cog(UtilCog(bot))