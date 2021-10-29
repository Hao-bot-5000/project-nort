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

class EconomyCog(BaseCog, name="Economy"):
    yash_coin_data_path = get_json_path("yash_coin")
    yash_coin_data = get_json_data(yash_coin_data_path)

    def __init__(self, bot):
        self.graph_url = None
        super().__init__(bot)

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

        member_data = self.get_member_data(ctx.guild, member)
        nort_bucks = dict_get_as_int(member_data, "nort_bucks")
        yash_coins = dict_get_as_int(member_data, "yash_coins")

        yash_coin_values = self.get_yash_coin_values(self.yash_coin_data)
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

        now = datetime.now()
        today = str(date.today())

        if self.yash_coin_data.get("prev_check", None) != today:
            # Generate new graph for new day
            try:
                old_values = self.get_yash_coin_values(self.yash_coin_data)
                new_values = self.create_yash_coin_values(old_values[-1])
            except ValueError:
                new_values = self.create_yash_coin_values()

            self.yash_coin_data["prev_check"] = today
            self.yash_coin_data["values"] = new_values

            set_json_data(self.yash_coin_path, self.yash_coin_data)

            indices = len(new_values)
            current_values = new_values[:self.get_current_yash_coin_index(indices) + 1]

            buffer = self.create_yash_coin_graph(current_values, indices)
        else:
            # Update graph values
            try:
                values = self.get_yash_coin_values(self.yash_coin_data)
            except ValueError:
                values = self.create_yash_coin_values()

            indices = len(values)
            current_values = values[:self.get_current_yash_coin_index(indices) + 1]

            if get_simple_graph_num_points() < len(current_values):
                buffer = self.update_yash_coin_graph(current_values, indices)
            else:
                buffer = None

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
        
        if not buffer:
            embed_reply.set_image(url=self.graph_url)
            await ctx.send(embed=embed_reply)
        else:
            file = discord.File(buffer, filename="plot.png")
            embed_reply.set_image(url="attachment://plot.png")
            message = await ctx.send(file=file, embed=embed_reply)
            self.graph_url = message.embeds[0].image.url



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

        cost = self.handle_investment(ctx, self.input_to_positive_int(amount))
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

        cost = self.handle_investment(ctx, -self.input_to_positive_int(amount))
        if cost is not None:
            await ctx.send(f"You received `{-cost}` NortBucks from selling YashCoins!")



    ### Helper Methods ###
    def get_yash_coin_values(self, yash_coin_data=None):
        """
            Return a list of YashCoin values stored inside ``yash_coin_data``. If
            ``yash_coin_data`` is not given, retrieve the YashCoin data from the
            ``yash_coin.json`` file.

            Parameters
            ----------
            yash_coin_data: :class:`dict`
                the data on YashCoins.
            
            Returns
            -------
            yash_coin_values: :class:`list`
                a list of the current YashCoin values.

            Raises
            ------
            ValueError:
                the YashCoin values could not be found inside ``yash_coin_data``.
        """

        if yash_coin_data is None:
            yash_coin_data = self.yash_coin_data

        yash_coin_values = dict_get_as_list(yash_coin_data, "values")
        if not yash_coin_values:
            raise ValueError("YashCoin values could not be properly retrieved")

        return yash_coin_values

    def get_current_yash_coin_index(self, size):
        """
            Return the index that points to the most current value of YashCoin, relative
            to the amount of time that has passed since the start of the current day.

            Parameters
            ----------
            size: :class:`int`
                the number of times the value of YashCoin changes per day.
            
            Returns
            -------
            index: :class:`int`
                an index pointing to a value stored inside a list of YashCoin values.

            Raises
            ------
            ValueError:
                ``size`` is not a positive value.\n
        """

        if size <= 0:
            raise ValueError("'size' must be a positive value")

        now = datetime.now()
        return int(size * ((now.hour + (now.minute / 60)) / 24))

    def create_yash_coin_values(self, start=1000, steps=96, mu=0, sigma=0.2,
                                lower=500, upper=1500):
        """
            Return a list of YashCoin values which somewhat imitates stock prices over
            time by using Geometric Brownian Motion.

            Parameters
            ----------
            start: :class:`int, optional`
                the starting value that the list will start with.
            steps: :class:`int, optional`
                the number of times the value of YashCoin will fluctuate.
            mu: :class:`float, optional`
                the amount of drift from the starting value, or the rate of growth.
            sigma: :class:`float, optional`
                the amount of variation across the values.
            lower: :class:`int, optional`
                the minimum value of ``start`` before ``mu`` is set to ``sigma`` to
                slightly prevent the value of YashCoin from further decreasing.
            upper: :class:`int, optional`
                the maximum value of ``start`` before ``mu`` is set to ``-sigma`` to
                slightly prevent the value of YashCoin from further increasing.
            
            Returns
            -------
            yash_coin_values: :class:`list`
                a calculated list of YashCoin values, with a length of ``1 + steps``.

            Raises
            ------
            ValueError:
                ``start`` is not a positive value.\n
                ``steps`` is a negative value.\n
                ``sigma`` is a negative value.\n
                ``lower`` is greater than or equal to ``upper``.\n
                ``lower`` or ``upper`` are not positive values.
        """

        if start <= 0:
            raise ValueError("'start' must be a positive value")
        if steps < 0:
            raise ValueError("'steps' must be a non-negative value")
        if sigma < 0:
            raise ValueError("'sigma' must be a non-negative value")
        if lower >= upper:
            raise ValueError("'lower' must be smaller than 'upper'")
        if upper <= 0:
            raise ValueError("'lower' and 'upper' must both be positive values")

        if start < lower: mu = sigma
        elif start > upper: mu = -sigma

        dy = 1 / steps
        dw = sqrt(dy) * random.randn(steps)
        increments = (mu - sigma * sigma / 2) * dy + sigma * dw
        values = [int(v) for v in start * cumprod(exp(increments))]
        return [start] + values

    def create_yash_coin_graph(self, values, indices):
        """
            Return a buffer referencing the newly generated YashCoin stock graph.

            Parameters
            ----------
            values: :class:`list[int]`
                a list of YashCoin values.
            indices: :class:`int`
                the number of YashCoin values given.
            
            Returns
            -------
            buffer: :class:`io.BytesIO`
                the buffer referencing the newly plotted graph.
        """

        color = self.get_yash_coin_line_color(values[0], values[-1])
        return create_simple_graph(None, values, xlim=(0, indices), color=color)

    def update_yash_coin_graph(self, new_values, indices):
        """
            Return a buffer referencing an updated YashCoin stock graph, based on the
            values given.

            Parameters
            ----------
            new_values: :class:`list[int]`
                a list of YashCoin values to replace the previous values.
            indices: :class:`int`
                the number of YashCoin values given.
            
            Returns
            -------
            buffer: :class:`io.BytesIO`
                the buffer referencing the updated graph.
        """

        color = self.get_yash_coin_line_color(new_values[0], new_values[-1])
        return update_simple_graph(None, new_values, xlim=(0, indices), color=color)

    def get_yash_coin_line_color(self, start, end):
        """
            Return a color based on the difference between the two given values. If
            there is no difference between the two values, the color will be gray. If
            the first value is smaller than the second value, the color will be green.
            If the first value is larger than the second value, the color will be red.

            Parameters
            ----------
            start: :class:`int`
                the initial value of YashCoin.
            end: :class:`int`
                the final value of YashCoin.
            
            Returns
            -------
            color: :class:`str`
                the line color used for the YashCoin stock graph.
        """

        if start == end: return "gray"
        return "green" if start < end else "red"

    async def handle_investment(self, ctx, amount):
        """
            Handle the transaction of YashCoins based on the given amount and return the
            number of NortBucks lost from the transaction. If the transaction results in
            an invalid currency value, such as a negative number, send a message through
            the context indicating the transaction could not be made, and return
            ``None``.

            Parameters
            ----------
            ctx: :class:`discord.Context`
                the current context for a command sent by a member.
            amount: :class:`int`
                the amount of YashCoins to add to a member's data.
            
            Returns
            -------
            value: :class:`int, None`
                the amount of NortBucks lost after the transaction if the transaction
                was successful, otherwise ``None``.
        """

        yash_coin_values = self.get_yash_coin_values(self.yash_coin_data)
        current_idx = self.get_current_yash_coin_index(len(yash_coin_values))
        current_value = yash_coin_values[current_idx]

        member_data = self.get_member_data(ctx.guild, ctx.author, default=True)

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

        set_json_data(self.data_path, self.data)
        return value


def setup(bot):
    bot.add_cog(EconomyCog(bot))

