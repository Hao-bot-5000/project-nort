import discord
from discord.ext        import commands

from utils              import (get_mentioned_member, dict_get_as_float, 
                                create_progress_bar)

from cogs.base_cog      import BaseCog
from custom_errors      import TooManyArgumentsError, MemberNotFoundError

class StatisticsCog(BaseCog, name="Statistics"):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(
        aliases=["cm"],
        brief="Displays cringe meter",
        description="Displays the member's cringe meter"
    )
    @commands.guild_only()
    async def cringemeter(self, ctx, member=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("cringemeter")

        target_member = (
            ctx.author if member is None else 
            get_mentioned_member(ctx.message, backup=member)
        )
        print(target_member)

        member_data = self.get_member_data(ctx.guild, target_member)
        cringe_meter = dict_get_as_float(member_data, "cringe_meter")
        percent, bar = create_progress_bar(cringe_meter)

        embed_reply = self.create_embed()
        embed_reply.set_author(
            name=f"{target_member.display_name}'s Cringe Meter:",
            icon_url=target_member.avatar_url
        )
        embed_reply.description = (
            f"**Status** `{self.get_cringe_status(percent)}`\n**{percent}%** `{bar}`"
        )

        await ctx.send(embed=embed_reply)



    ### Helper Methods ###
    CRINGE_STATUSES = ("Not Cringe", "Kinda Cringe", "Cringe", "Ultra Cringe", "YASH")

    def get_cringe_status(self, percent):
        """
            Return a status based on the given percentage value.

            Parameters
            ----------
            percent: :class:`int`
                an integer representation of a percentage value.

            Returns
            -------
            status: :class:`str`
                the calculated status.

            Raises
            ------
            ValueError:
                ``percent`` is not between ``0`` and ``100``.
        """

        if percent < 0 or percent > 100:
            raise ValueError("'percent' must be between '0' and '100'")

        if percent == 69: return "Nice"
        return self.CRINGE_STATUSES[int(percent / 100 * (len(self.CRINGE_STATUSES) - 1))]
        


def setup(bot):
    bot.add_cog(StatisticsCog(bot))