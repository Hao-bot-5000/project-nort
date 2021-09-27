import discord
from discord.ext import commands

from cogs.base_cog import BaseCog

from utils import (JSON_DATA_PATH, get_json_data, set_json_data,
                   get_emoji, get_mentioned_member, create_progress_bar,
                   create_black_embed)

import asyncio

from datetime import date


class ExpeditionCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Expedition")

    ### Expedition Command ###
    @commands.command(
        aliases=["exp", "quest"],
        brief="Go on expedition",
        description="Starts an expedition to gather NortCoins (default 1 hour) Usage: !nort exp 3h, 6h, 12h"
    )
    @commands.guild_only()
    async def expedition(self, ctx, *args):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})

        author_data = yc_members_data.get(author_id, {})
        time = ''
        if len(args) > 1:
            await ctx.send("Too many arguments. Please enter: 3h, 6h, 12h or leave blank for 1h")
            return
        if 'help' in args:
            await ctx.send("Usage: !nort exp __ (blank for 1h, 3h, 6h, 12h)")
            return

        if author_data["on_expedition"] == 0:
            author_data["on_expedition"] = 1
            if len(args) == 0:
                time = '1h'
            time = str(args[0])
            asyncio.create_task(self.inner(ctx, author_data, json_data, time))
            await ctx.send("Expedition started!")
            await set_json_data(JSON_DATA_PATH, json_data)
        else:
            await ctx.send("Currently on expedition!")

    async def inner(self, ctx, author_data, json_data, time):
        if str(time) == '3h':
            await asyncio.sleep(5)
            author_data["nort_coins"] += 3
        elif str(time) == '6h':
            await asyncio.sleep(10)
            author_data["nort_coins"] += 5
        elif str(time) == '12h':
            await asyncio.sleep(15)
            author_data["nort_coins"] += 100
        else:
            await asyncio.sleep(2)
            author_data["nort_coins"] += 1000
        await ctx.send("Expedition completed!")
        author_data["on_expedition"] = 0
        await set_json_data(JSON_DATA_PATH, json_data)

    ### Daily Claim Command ###
    @commands.command(
        brief="Claim daily NortCoins",
        description="Claim daily NortCoins"
    )
    @commands.guild_only()
    async def daily(self, ctx, *args):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})

        author_data = yc_members_data.get(author_id, {})
        if author_data.get('prev_daily', '-1') != str(date.today()):
            nort_coins = author_data.get("nort_coins", 0)
            author_data["yash_coins"] += 100
            author_data["prev_daily"] = str(date.today())
            await ctx.send("Daily YashCoins claimed!")
        else:
            await ctx.send("Daily already claimed!")

        await set_json_data(JSON_DATA_PATH, json_data)


def setup(bot):
    bot.add_cog(ExpeditionCog(bot))
