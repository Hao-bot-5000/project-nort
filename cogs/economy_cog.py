import discord
from discord.ext        import commands

from datetime           import datetime, date
from numpy              import random, exp, linspace, cumprod
from math               import sqrt

from utils              import (get_json_path, get_json_data, set_json_data,
                                get_emoji, create_simple_graph, update_simple_graph,
                                get_simple_graph_num_points, get_mentioned_member, 
                                dict_get_as_int, dict_get_as_list)

from cogs.base_cog      import BaseCog
from custom_errors      import TooManyArgumentsError, MemberNotFoundError

class EconomyCog(BaseCog):
    def __init__(self, bot):
        self.yash_coin_path = get_json_path("yash_coin")
        super().__init__(bot, category="Economy")

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

        member_name = member
        member = (
            ctx.author if member is None else 
            await get_mentioned_member(ctx.message, backup=member)
        )

        if member is None:
            raise MemberNotFoundError(member_name)

        member_data = await self.get_member_data(ctx.guild, member)
        nort_bucks = dict_get_as_int(member_data, "nort_bucks")
        yash_coins = dict_get_as_int(member_data, "yash_coins")

        yash_coin_values = await self.get_yash_coin_values()
        current_idx = self.get_current_yash_coin_index(len(yash_coin_values))
        current_value = yash_coin_values[current_idx]
        
        embed_reply = self.create_embed()
        embed_reply.set_author(
            name=f"{member.display_name}'s Balance:",
            icon_url=member.avatar_url
        )
        embed_reply.add_field(
            name=f"**YashCoins** {get_emoji(':coin:')}",
            value=f"`{yash_coins}`",
            inline=True
        )
        embed_reply.add_field(
            name=f"**NortBucks** {get_emoji(':dollar:')}",
            value=f"`{nort_bucks}`",
            inline=True
        )
        embed_reply.add_field(
            name=f"**Total** {get_emoji(':moneybag:')}",
            value=f"`{nort_bucks + (yash_coins * current_value)} " +
                  f"({nort_bucks} NRT + {current_value}x{yash_coins} YSH)`", 
            inline=False
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

        yash_coin_data = await get_json_data(self.yash_coin_path)

        now = datetime.now()
        today = str(date.today())

        if yash_coin_data.get("prev_check", None) != today:
            # Generate new graph for new day
            try:
                old_values = await self.get_yash_coin_values(yash_coin_data)
                new_values = self.create_yash_coin_values(old_values[-1])
            except ValueError:
                new_values = self.create_yash_coin_values()

            yash_coin_data["prev_check"] = today
            yash_coin_data["values"] = new_values

            await set_json_data(self.yash_coin_path, yash_coin_data)

            indices = len(new_values)
            current_values = new_values[:self.get_current_yash_coin_index(indices) + 1]

            self.create_yash_coin_graph(current_values, indices)
        else:
            # Update graph values
            try:
                values = await self.get_yash_coin_values(yash_coin_data)
            except ValueError:
                values = self.create_yash_coin_values()

            indices = len(values)
            current_values = values[:self.get_current_yash_coin_index(indices) + 1]

            if get_simple_graph_num_points() < len(current_values):
                self.update_yash_coin_graph(current_values, indices)

        difference = current_values[-1] - current_values[0]
        percentage = difference / current_values[0]

        embed_reply = self.create_embed()
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

        cost = await self.handle_investment(ctx, self.input_to_positive_int(amount))
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
            raise TooManyArgumentsError("divest")

        gain = -(await self.handle_investment(ctx, -self.input_to_positive_int(amount)))
        if gain is not None:
            await ctx.send(f"You received `{gain}` NortBucks from selling YashCoins!")



    ### Helper Methods ###
    async def get_yash_coin_values(self, yash_coin_data=None):
        if yash_coin_data is None:
            yash_coin_data = await get_json_data(self.yash_coin_path)

        yash_coin_values = dict_get_as_list(yash_coin_data, "values")
        if not yash_coin_values:
            raise ValueError("YashCoin values could not be properly retrieved")

        return yash_coin_values
    
    def get_current_yash_coin_index(self, size):
        now = datetime.now()
        return int(size * ((now.hour + (now.minute / 60)) / 24))

    def create_yash_coin_values(self, initial=1000, steps=96, mu=0.05, sigma=0.2):
        dy = 1 / steps
        dw = sqrt(dy) * random.randn(steps)
        increments = (mu - sigma * sigma / 2) * dy + sigma * dw
        scales = self.create_yash_coin_scales(initial, steps)
        values = [int(s * v) for s, v in zip(scales, cumprod(exp(increments)))]
        return [initial] + values

    def create_yash_coin_scales(self, initial, steps, min=500, max=1500):
        if initial < max and initial > min:
            return [initial] * steps

        return linspace(initial, max if initial > max else min, steps).tolist()

    def create_yash_coin_graph(self, values, indices):
        color = self.get_yash_coin_line_color(values[0], values[-1])
        create_simple_graph(None, values, xlim=(0, indices), color=color)
    
    def update_yash_coin_graph(self, new_values, indices):
        color = self.get_yash_coin_line_color(new_values[0], new_values[-1])
        update_simple_graph(None, new_values, xlim=(0, indices), color=color)

    def get_yash_coin_line_color(self, start, end):
        if start == end: return "gray"
        return "green" if start < end else "red"

    async def handle_investment(self, ctx, amount):
        yash_coin_values = await self.get_yash_coin_values()
        current_idx = self.get_current_yash_coin_index(len(yash_coin_values))
        current_value = yash_coin_values[current_idx]

        data = await self.get_data()
        guild_data = await self.get_guild_data(ctx.guild, data)
        member_list_data = await self.get_member_list_data(ctx.guild, guild_data)
        member_data = await self.get_member_data(ctx.guild, ctx.author, member_list_data)

        nort_bucks = dict_get_as_int(member_data, "nort_bucks", 0)
        yash_coins = dict_get_as_int(member_data, "yash_coins", 0)

        value = amount * current_value

        if amount > 0 and nort_bucks < value:
            await ctx.send(
                f"You do not have the required `{value}` " + 
                "NortBucks to make this investment"
            )
            return None

        if amount < 0 and yash_coins < -amount:
            await ctx.send(
                f"You do not have the required `{-amount}` " + 
                "YashCoins to make this divestment"
            )
            return None

        member_data["nort_bucks"] = nort_bucks - value
        member_data["yash_coins"] = yash_coins + amount

        await set_json_data(self.data_path, data)
        return value


def setup(bot):
    bot.add_cog(EconomyCog(bot))

