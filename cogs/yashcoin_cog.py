import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from utils              import (get_json_path, get_json_data, set_json_data,
                                get_emoji, get_mentioned_member, create_progress_bar,
                                create_black_embed, create_stock_graph, 
                                update_stock_graph, get_stock_graph_value_count)
from custom_errors import TooManyArgumentsError

from numpy import random, exp, cumprod
from math import sqrt
from datetime import datetime, date

class YashCoinCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="YashCoin")

    ### Initiate command ###
    @commands.command(
        aliases=["init", "join"],
        brief="Enters YashCoin event",
        description="Adds yourself to the YashCoin event"
    )
    @commands.guild_only()
    async def initiate(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("initiate")

        guild_id = str(ctx.guild.id)
        author_id = str(ctx.author.id)

        # Retrieve json contents
        path = get_json_path("data")
        json_data = await get_json_data(path)
        guild_data = json_data.setdefault(guild_id, {})
        yc_members_data = guild_data.setdefault("yc_members", {})

        # Update contents of json file if author id does not yet exist
        if author_id not in yc_members_data:
            yc_members_data[author_id] = {
                "nort_bucks" : 0,
                "yash_coins" : 0,
                "cringe_meter" : 0,
                "prev_daily" : None,
                "on_expedition": 0
            }
            await set_json_data(path, json_data)

            reply = f"Thank you for joining YashCoin {get_emoji(':tm:')} Incorporated!"
        else:
            reply = f"You are already a member of YashCoin {get_emoji(':tm:')} Incorporated"

        await ctx.send(reply)

    ### Balance command ###
    @commands.command(
        aliases=["bal"],
        brief="Displays balance",
        description="Displays the member's current balance"
    )
    @commands.guild_only()
    async def balance(self, ctx, member=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("balance")

        member = await self.__get_yc_member(ctx, member if member else ctx.author)

        if member is None:
            return # Error messages are handled inside the private func

        nortcoins = member.get("data", {}).get("nort_bucks", 0)
        yashcoins = member.get("data", {}).get("yash_coins", 0)

        values = (await get_json_data(get_json_path("yashcoin"))).get("values", None)

        if not values:
            await ctx.send("Stock data could not be found")
            return

        current_value = values[self.__get_clock_index(len(values), datetime.now())]

        embed_reply = create_black_embed()

        embed_reply.set_author(
            name=f"{member.get('display_name', 'Member')}'s Balance:",
            icon_url=member.get("icon", None)
        )
        embed_reply.add_field(
            name=f"**YashCoins** {get_emoji(':coin:')}",
            value=f"`{yashcoins}`",
            inline=True
        )
        embed_reply.add_field(
            name=f"**NortBucks** {get_emoji(':dollar:')}",
            value=f"`{nortcoins}`",
            inline=True
        )
        embed_reply.add_field(
            name=f"**Total** {get_emoji(':moneybag:')}",
            value=f"`{nortcoins + (yashcoins * current_value)} " +
                  f"({nortcoins} NRT + {current_value}x{yashcoins} YSH)`", 
            inline=False
        )

        await ctx.send(embed=embed_reply)

    ### CM Command ###
    @commands.command(
        aliases=["cm"],
        brief="Displays cringe meter",
        description="Displays the member's cringe meter"
    )
    @commands.guild_only()
    async def cringemeter(self, ctx, member=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("cringemeter")

        member = await self.__get_yc_member(ctx, member if member else ctx.author)

        if member is None:
            return # Error messages are handled inside the private func

        cringe_meter_value = member.get("data", {}).get("cringe_meter", 0)
        cringe_meter_status = self.__get_cringe_status(cringe_meter_value)
        cringe_meter_bar = create_progress_bar(cringe_meter_value)

        embed_reply = create_black_embed()

        embed_reply.set_author(
            name=f"{member.get('display_name', 'Member')}'s Cringe Meter:",
            icon_url=member.get("icon", None)
        )
        embed_reply.description = (
            f"**Status** `{cringe_meter_status}`\n" +
            f"**{cringe_meter_bar[0]}%** `{cringe_meter_bar[1]}`"
        )

        await ctx.send(embed=embed_reply)

    ### Stocks Command ###
    @commands.command(
        aliases=["stonks"],
        brief="Displays YashCoin values",
        description="Displays the current YashCoin conversion rate"
    )
    @commands.guild_only()
    async def stocks(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("stocks")

        path = get_json_path("yashcoin")
        json_data = await get_json_data(path)

        now = datetime.now()
        today = str(date.today())

        if json_data.get("prev_check", None) != today:
            # Generate new graph for new day
            try:
                old_values = json_data.get("values", [self.__BASE_PRICE])
                new_values = self.__generate_yc_values(old_values[-1])
                if not isinstance(old_values, list): raise TypeError()
            except (TypeError, IndexError):
                new_values = self.__generate_yc_values()

            json_data["prev_check"] = today
            json_data["values"] = new_values

            await set_json_data(path, json_data)

            indices = len(new_values)
            current_values = new_values[:self.__get_clock_index(indices, now) + 1]

            self.__create_yc_graph(current_values, indices)
        else:
            # Update graph values
            try:
                values = json_data.get("values", [self.__BASE_PRICE])
                if not isinstance(values, list): raise TypeError()
            except TypeError:
                values = [self.__BASE_PRICE]

            indices = len(values)
            current_values = values[:self.__get_clock_index(indices, now) + 1]

            if get_stock_graph_value_count() < len(current_values):
                self.__update_yc_graph(current_values, indices)

        difference = current_values[-1] - current_values[0]
        percentage = difference / current_values[0]

        embed_reply = create_black_embed()

        embed_reply.title = "Market Summary — `YCSE: YSH`"
        embed_reply.add_field(
            name="**Value**", 
            value=f"`{current_values[-1]} NRT` | `{difference:+d} ({percentage:+.2%})`", 
            inline=False
        )
        embed_reply.add_field(
            name="**Date and Time**", 
            value=f"`{now.strftime('%b %d, %I:%M %p')} PT`", 
            inline=False
        )
        file = discord.File("assets/plot.png", filename="plot.png")
        embed_reply.set_image(url="attachment://plot.png")

        await ctx.send(file=file, embed=embed_reply)

    ### Invest Command ###
    @commands.command(
        aliases=["buy"],
        brief="Invest into YashCoin",
        description="Buy the given number of YashCoin shares using NortBucks"
    )
    @commands.guild_only()
    async def invest(self, ctx, amount=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("invest")

        try:
            amount = int(amount) if amount is not None else 1
            if amount < 1: raise ValueError()
        except ValueError:
            await ctx.send("Please provide a valid positive number")
            return

        cost = await self.__handle_investment(ctx, amount)
        if cost is not None:
            await ctx.send(f"Thank you for investing `{cost}` NortBucks into YashCoin!")
    
    ### Divest Command ###
    @commands.command(
        aliases=["sell"],
        brief="Divest from YashCoin",
        description="Sell the given number of YashCoin shares for NortBucks"
    )
    @commands.guild_only()
    async def divest(self, ctx, amount=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("invest")

        try:
            amount = int(amount) if amount is not None else 1
            if amount < 1: raise ValueError()
        except ValueError:
            await ctx.send("Please provide a valid positive number")
            return

        value = await self.__handle_investment(ctx, -amount)
        if value is not None:
            await ctx.send(f"Thank you for trading in your `{-value}` NortBucks!")



    ### Private methods ###
    # Returns None if member cannot be found in the guild
    # Returns None if member is found in the guild, but not in the JSON file
    # Returns a dict containing the member's data and display name if member is found
    async def __get_yc_member(self, ctx, member):
        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        path = get_json_path("data")
        json_data = await get_json_data(path)
        guild_data = json_data.get(guild_id, None)
        yc_members_data = guild_data.get("yc_members", None) if guild_data else None

        if member != ctx.author:
            result = await get_mentioned_member(ctx.message, backup=member)
            if result is None:
                await ctx.send(f"Member {member} could not be found")
                return None
            else:
                member = result

        member_id = str(member.id)
        member_data = yc_members_data.get(member_id, None) if yc_members_data else None

        if not member_data:
            await ctx.send(
                (f"{member.display_name} is " if member != ctx.author else "You are ") +
                f"not a member of YashCoin{get_emoji(':tm:')} Incorporated"
            )
            return None

        return {
            "data" : member_data,
            "display_name" : member.display_name,
            "icon" : member.avatar_url
        }

    __CRINGE_STATUSES = ("Not Cringe", "Kinda Cringe", "Cringe", "Ultra Cringe", "YASH")
    def __get_cringe_status(self, percent):
        if percent == 0.69: return "Nice"
        return self.__CRINGE_STATUSES[int(percent * (len(self.__CRINGE_STATUSES) - 1))]

    # NOTE: formula from https://stackoverflow.com/a/8609519
    __BASE_PRICE = 1000
    __MIN_SCALE = 300
    __MAX_SCALE = 1500
    # initial    - starting value of graph
    # steps      - number of values along the graph (not including initial)
    # mu & sigma - constants that affect the values
    def __generate_yc_values(self, initial=__BASE_PRICE, steps=96, mu=0.05, sigma=0.2):
        dy = 1 / steps
        dw = sqrt(dy) * random.randn(steps)
        increments = (mu - sigma * sigma / 2) * dy + sigma * dw
        scale = min(self.__MAX_SCALE, max(self.__MIN_SCALE, initial))
        values = [int(v) for v in scale * cumprod(exp(increments))]
        return [initial] + values
    
    __X_PADDING = 0.05
    def __create_yc_graph(self, values, indices):
        xlim = (-self.__X_PADDING * indices, (1 + self.__X_PADDING) * indices)
        color = self.__get_yc_graph_color(values[0], values[-1])
        create_stock_graph(None, values, xlim=xlim, color=color)
    
    def __update_yc_graph(self, new_values, indices):
        xlim = (-self.__X_PADDING * indices, (1 + self.__X_PADDING) * indices)
        color = self.__get_yc_graph_color(new_values[0], new_values[-1])
        update_stock_graph(None, new_values, xlim=xlim, color=color)

    def __get_yc_graph_color(self, start, end):
        if start == end:
            return "gray"
        
        return "green" if start < end else "red"

    async def __handle_investment(self, ctx, amount):
        values = (await get_json_data(get_json_path("yashcoin"))).get("values", None)

        if not values:
            await ctx.send("Stock data could not be found")
            return None

        current_value = values[self.__get_clock_index(len(values), datetime.now())]

        data_path = get_json_path("data")
        json_data = await get_json_data(data_path)
        guild_data = json_data.setdefault(str(ctx.guild.id), {})
        yc_members_data = guild_data.setdefault("yc_members", {})
        member_data = yc_members_data.setdefault(str(ctx.author.id), {})

        nortcoins = member_data.get("nort_bucks", 0)
        yashcoins = member_data.get("yash_coins", 0)

        value = amount * current_value

        if amount > 0 and nortcoins < value:
            await ctx.send(
                f"You do not have the required `{value}` " + 
                "NortBucks to make this investment"
            )
            return None

        if amount < 0 and yashcoins < -amount:
            await ctx.send(
                f"You do not have the required `{-amount}` " + 
                "YashCoins to make this divestment"
            )
            return None

        print(value, amount, yashcoins)
        member_data["nort_bucks"] = nortcoins - value
        member_data["yash_coins"] = yashcoins + amount

        await set_json_data(data_path, json_data)

        return value

    def __get_clock_index(self, indices, now):
        return int(indices * ((now.hour + (now.minute / 60)) / 24))


def setup(bot):
    bot.add_cog(YashCoinCog(bot))
