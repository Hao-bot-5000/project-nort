import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from discord.errors     import ClientException
from custom_errors      import TooManyArgumentsError

class MusicCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Music")

    @commands.command(
        aliases=["p"],
        brief="Plays music",
        description="Joins the channel and plays music"
    )
    @commands.guild_only()
    async def play(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("play")

        if ctx.author.voice == None:
            await ctx.send("You are not in a voice channel")
            return

        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send("playing music")
        except ClientException:
            await ctx.send("NortBot is in a different voice channel")

    @commands.command(
        aliases=["s"],
        brief="Stops music",
        description="Stops music and leaves the channel"
    )
    @commands.guild_only()
    async def stop(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("play")

        if ctx.voice_client == None:
            await ctx.send("NortBot is not in a voice channel")
            return

        if ctx.author.voice == None:
            await ctx.send("You are not in a voice channel")
            return

        if ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("NortBot is in a different voice channel")


def setup(bot):
    bot.add_cog(MusicCog(bot))