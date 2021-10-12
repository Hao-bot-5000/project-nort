import discord
from discord.ext import commands

from cogs.base_cog import BaseCog

from utils import (get_json_path, get_json_data, set_json_data,
                   get_emoji, get_mentioned_member, create_progress_bar,
                   create_black_embed)
from custom_errors import MemberNotFoundError, TooManyArgumentsError

import asyncio

from datetime import date


class ExpeditionCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Expedition")

    ### Daily Claim Command ###
    @commands.command(
        brief="Claim 600 daily NortBucks",
        description="Claim 600 daily NortBucks every day (PST Time)"
    )
    @commands.guild_only()
    async def daily(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("daily")

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        path = get_json_path("data")
        json_data = await get_json_data(path)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})

        author_data = yc_members_data.get(author_id, None)

        if author_data is None:
            raise MemberNotFoundError()

        today = str(date.today())
        if author_data.get("prev_daily", None) != today:

            author_data["nort_bucks"] = self.__add_coins(author_data, "nort_bucks", 600)
            author_data["prev_daily"] = today
            await ctx.send("Daily NortBucks successfully claimed!")
        else:
            await ctx.send("Daily NortBucks already claimed!")

        await set_json_data(path, json_data)

    ### Expedition Command ###
    @commands.command(
        aliases=["exp", "quest"],
        brief="Go on expedition to find NortBucks",
        description="Start an expedition based on the given timescale "
                    "(short, normal, long)"
    )
    @commands.guild_only()
    async def expedition(self, ctx, timescale="short", *args):
        # Checking for arguements
        if len(args) > 0:
            raise TooManyArgumentsError("expedition")

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        path = get_json_path("data")
        json_data = await get_json_data(path)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})

        author_data = yc_members_data.get(author_id, None)

        if author_data is None:
            raise MemberNotFoundError()
        
        if author_data.get("on_expedition", 0) == 0:
            await self.__start_expedition(ctx, author_data, json_data, timescale)
        else:
            await ctx.send("Currently on expedition!")



    ### Private Methods ###
    __TIMES = ("short", "normal", "long")
    __REWARDS = (100, 250, 700)
    __DURATIONS = (10, 30, 90)
    async def __start_expedition(self, ctx, author_data, json_data, timescale):
        if timescale not in self.__TIMES:
            await ctx.send(f"Please input a valid timescale ({', '.join(self.__TIMES)})")
            return

        author_data["on_expedition"] = 1
        await set_json_data(get_json_path("data"), json_data)
        await ctx.send("Expedition started!")

        idx = self.__TIMES.index(timescale)

        await asyncio.sleep(self.__DURATIONS[idx])

        author_data["nort_bucks"] = self.__add_coins(
            author_data, "nort_bucks", self.__REWARDS[idx]
        )

        author_data["on_expedition"] = 0
        await set_json_data(get_json_path("data"), json_data)
        await ctx.send(f"{ctx.author.mention}\nYour expedition has completed!")

    def __add_coins(self, member_data, coin_type, amount):
        # When modifying existing data based on its previous value,
        # check that the value's data type is valid (assume 0 if invalid)
        try:
            return int(member_data.get(coin_type, 0)) + amount
        except TypeError:
            return amount


def setup(bot):
    bot.add_cog(ExpeditionCog(bot))