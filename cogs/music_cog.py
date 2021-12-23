import discord
from discord.ext                import commands

from cogs.base_cog              import BaseCog

class MusicCog(BaseCog, name="Music"):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(
        aliases=["p"],
        brief="Plays music",
        description="Joins the channel and plays music",
        ignore_extra=False
    )
    @commands.guild_only()
    async def play(self, ctx):
        if ctx.author.voice == None:
            await ctx.send("You are not in a voice channel")
            return

        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send("playing music")
        except discord.ClientException:
            await ctx.send("NortBot is in a different voice channel")

    @commands.command(
        aliases=["s", "l", "leave"],
        brief="Stops music",
        description="Stops music and leaves the channel",
        ignore_extra=False
    )
    @commands.guild_only()
    async def stop(self, ctx):
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
