import discord
from discord import channel
from discord import client
from discord.errors import ClientException
from discord.ext import commands
from discord.ext.commands import context
from cogs.base_cog import BaseCog
from custom_errors import TooManyArgumentsError

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
        if ctx.author.voice == None:
            await ctx.send("User not in a voice call")
            return
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send("playing music")
        except ClientException:
            await ctx.send("Nortbot is in a different channel")
        #case 1: user not in a call
        #case 2: bot is in a different call
        #case 3: bot has no perms

    @commands.command(
        aliases=["l"],
        brief="Leaves channel",
        description="Leaves the channel"
    )
    @commands.guild_only()
    async def leave(self, ctx, *args):
        if ctx.voice_client == None:
            await ctx.send("Nort bot not in the call")
            return
        if ctx.author.voice == None:
            await ctx.send("You are not in this call")
            return
        if ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Nort bot is in a different channel")

        #case 1: bot is not in call
        #case 2: user not in same call as bot

def setup(bot):
    bot.add_cog(MusicCog(bot))