import discord
from discord.ext        import commands

from random             import uniform, randint
from utils              import (get_json_path, get_json_data, dict_get_as_list,
                                get_mentioned_member)

from cogs.base_cog      import BaseCog
from custom_errors      import TooManyArgumentsError, MemberNotFoundError

class NortMonsCog(BaseCog, name="NortMons"):
    nort_mons_data_path = get_json_path("nort_mons")
    nort_mons_data = get_json_data(nort_mons_data_path)

    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(
        brief="Catch NortMon",
        description="Catch yourself a Nortmon of a random rarity from the wild"
    )
    @commands.guild_only()
    async def catch(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("catch")

        await ctx.send(self.get_random_nort_mon())
        # TODO: attach NortMon id to member's data

    @commands.command(
        brief="Release NortMon",
        description="Release your current NortMon into the wild"
    )
    @commands.guild_only()
    async def release(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("release")

        await ctx.send("hello :)")
        # TODO: remove NortMon from member's data

    @commands.command(
        brief="Display NortMon",
        description="Display a member's current NortMon"
    )
    @commands.guild_only()
    async def nortmon(self, ctx, member=None, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("nortmon")

        member_name = member
        member = (
            ctx.author if member is None else 
            await get_mentioned_member(ctx.message, backup=member)
        )

        if member is None:
            raise MemberNotFoundError(member_name)

        member_data = self.get_member_data(ctx.guild, member)
        nort_mon_id = member_data.get("nort_mon", "rare-1") # TODO: create dict_get_as_str method?
        rarity, idx = nort_mon_id.split("-")

        # TODO: show member's NortMon if they currently have one
        nort_mon_data = dict_get_as_list(self.nort_mons_data, rarity)[int(idx)]
        name = nort_mon_data.get("name")
        hit_points = nort_mon_data.get("hit_points")
        attack_power = nort_mon_data.get("attack_power")
        speed = nort_mon_data.get("speed")
        image_url = nort_mon_data.get("image") or self.bot.user.avatar_url

        embed_reply = self.create_embed()
        embed_reply.set_author(
            name=f"{member.display_name}'s NortMon:",
            icon_url=member.avatar_url
        )
        embed_reply.add_field(
            name=f"**{rarity.capitalize()} — {name}**",
            value=f"**HP**: `{hit_points}`\n"
                  f"**ATK**: `{attack_power}`\n"
                  f"**SPD**: `{speed}`",
            inline=False
        )
        embed_reply.set_image(url=image_url)

        await ctx.send(embed=embed_reply)



    # Helper Methods #
    NORT_MON_WEIGHTS = { "legendary": 0.01, "rare": 0.04, "common": 0.2, "useless": 0.8 }

    def get_random_nort_mon(self):
        rand_weight = uniform(0, next(reversed(self.NORT_MON_WEIGHTS.values())))

        for rarity, weight in self.NORT_MON_WEIGHTS.items():
            if rand_weight <= weight:
                nort_mons_by_rarity = dict_get_as_list(self.nort_mons_data, rarity)
                rand_idx = randint(0, len(nort_mons_by_rarity) - 1)
                return f"{rarity}-{rand_idx}"


def setup(bot):
    bot.add_cog(NortMonsCog(bot))
