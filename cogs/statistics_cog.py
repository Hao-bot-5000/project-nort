import discord
from discord.ext        import commands

from utils              import (get_mentioned_member, dict_get_as_float, 
                                create_progress_bar)

from cogs.base_cog      import BaseCog
from custom_errors      import TooManyArgumentsError, MemberNotFoundError

class StatisticsCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Statistics")

    @commands.command(
        aliases=["cm"],
        brief="Displays cringe meter",
        description="Displays the member's cringe meter"
    )
    @commands.guild_only()
    async def cringemeter(self, ctx, member=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("cringemeter")

        member = (
            ctx.author if member is None else 
            await get_mentioned_member(ctx.message, backup=member)
        )

        if member is None:
            raise MemberNotFoundError(member)

        member_data = await self.get_member_data(ctx.guild, member)
        cringe_meter = dict_get_as_float(member_data, "cringe_meter")
        percent, bar = create_progress_bar(cringe_meter)

        embed_reply = self.create_embed()
        embed_reply.set_author(
            name=f"{member.display_name}'s Cringe Meter:",
            icon_url=member.avatar_url
        )
        embed_reply.description = (
            f"**Status** `{self.get_cringe_status(percent)}`\n**{percent}%** `{bar}`"
        )

        await ctx.send(embed=embed_reply)



    ### Helper Methods ###
    CRINGE_STATUSES = ("Not Cringe", "Kinda Cringe", "Cringe", "Ultra Cringe", "YASH")

    def get_cringe_status(self, percent):
        if percent == 69: return "Nice"
        return self.CRINGE_STATUSES[int(percent / 100 * (len(self.CRINGE_STATUSES) - 1))]
        


def setup(bot):
    bot.add_cog(StatisticsCog(bot))