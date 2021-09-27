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
        description="Starts an expedition to gather NortCoins after a certain time"
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
        if author_data["on_expedition"] == 0:
            author_data["on_expedition"] = 1
            await ctx.send("Expedition started!")
            asyncio.create_task(self.inner(ctx, author_data, json_data))
            await set_json_data(JSON_DATA_PATH, json_data)
        else:
            await ctx.send("Currently on expedition!")

    async def inner(self, ctx, author_data, json_data):

        await asyncio.sleep(10)
        await ctx.send("Expedition completed!")
        author_data["nort_coins"] += 100
        author_data["on_expedition"] = 0
        await set_json_data(JSON_DATA_PATH, json_data)

    ### Daily Claim Command ###
    @commands.command(
        brief="Claim daily YashCoins",
        description="Claim daily YashCoins"
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
