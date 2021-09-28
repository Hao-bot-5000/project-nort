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
    
    ### Daily Claim Command ###
    @commands.command(
        brief="Claim 600 daily NortCoins",
        description="Claim 600 daily NortCoins every day (PST Time)"
    )
    @commands.guild_only()
    async def daily(self, ctx, *args):
        if len(args) > 0:
            await ctx.send("Too many arguments")
            return

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})

        author_data = yc_members_data.get(author_id, {})

        today = str(date.today())
        if author_data.get("prev_daily", None) != today:
            # When modifying existing data based on its previous value, 
            # check that the value's data type is valid
            try:
                current_nortcoins = int(author_data.get("nort_coins", 0))
            except TypeError:
                current_nortcoins = 0

            author_data["nort_coins"] = current_nortcoins + 600
            author_data["prev_daily"] = today
            await ctx.send("Daily NortCoins successfully claimed!")
        else:
            await ctx.send("Daily NortCoins already claimed!")

        await set_json_data(JSON_DATA_PATH, json_data)

    ### Expedition Command ###
    @commands.command(
        aliases=["exp", "quest"],
        brief="Go on expedition to find NortCoins",
        description="Start an expedition based on the given timescale (short, normal, long)"
    )
    @commands.guild_only()
    async def expedition(self, ctx, timescale=None, *args):
        # Checking for arguements
        if len(args) > 0:
            await ctx.send("Too many arguments")
            return

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, {})
        yc_members_data = guild_data.get("yc_members", {})
        author_data = yc_members_data.get(author_id, {})
        
        if timescale is None: timescale = "short"

        if author_data.get("on_expedition", 0) == 0:
            asyncio.create_task(self.__start_expedition(ctx, author_data, json_data, timescale))
        else:
            await ctx.send("Currently on expedition!")
    


    ### Private Methods ###
    __TIMES = ("short", "normal", "long")
    __REWARDS = (100, 250, 625)
    __DURATIONS = (10, 20, 40)
    async def __start_expedition(self, ctx, author_data, json_data, timescale):
        if timescale not in self.__TIMES:
            await ctx.send(f"Please input a valid timescale ({', '.join(self.__TIMES)})")
            return

        author_data["on_expedition"] = 1
        await set_json_data(JSON_DATA_PATH, json_data)
        await ctx.send("Expedition started!")

        time_idx = self.__TIMES.index(timescale)

        await asyncio.sleep(self.__DURATIONS[time_idx])

        # When modifying existing data based on its previous value, 
        # check that the value's data type is valid
        try:
            current_nortcoins = int(author_data.get("nort_coins", 0))
        except TypeError:
            current_nortcoins = 0

        author_data["nort_coins"] = current_nortcoins + self.__REWARDS[time_idx]
        
        author_data["on_expedition"] = 0
        await set_json_data(JSON_DATA_PATH, json_data)
        await ctx.send(f"{ctx.author.mention}\nYour expedition has completed!")


def setup(bot):
    bot.add_cog(ExpeditionCog(bot))
