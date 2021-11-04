import discord
from discord.ext        import commands

from random             import uniform, randint
from utils              import (get_json_path, get_json_data, set_json_data,
                                dict_get_as_list, get_mentioned_member)

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

        member_data = self.get_member_data(ctx.guild, ctx.author, default=True)
        member_nort_mon = member_data.get("nort_mon")

        if member_nort_mon is not None:
            await ctx.send("You already own a NortMon")
            return
        
        nort_mon_name, nort_mon_id = self.get_random_nort_mon()
        rarity, _ = nort_mon_id.split("-")

        member_data["nort_mon"] = nort_mon_id
        set_json_data(self.data_path, self.data)

        await ctx.send(
            f"You've caught **{nort_mon_name}** — a `{rarity.capitalize()}` NortMon!"
        )

    @commands.command(
        brief="Release NortMon",
        description="Release your current NortMon into the wild"
    )
    @commands.guild_only()
    async def release(self, ctx, *args):
        if len(args) > 0:
            raise TooManyArgumentsError("release")

        member_data = self.get_member_data(ctx.guild, ctx.author)
        member_nort_mon = member_data.get("nort_mon")

        if member_nort_mon is None:
            await ctx.send("You do not own a NortMon")
            return

        member_data["nort_mon"] = None
        set_json_data(self.data_path, self.data)

        rarity, idx = member_nort_mon.split("-")
        nort_mon_name = dict_get_as_list(self.nort_mons_data, rarity)[int(idx)].get("name")

        await ctx.send(
            f"You've released your `{rarity.capitalize()}` **{nort_mon_name}**"
        )

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
        nort_mon_id = member_data.get("nort_mon") # TODO: create dict_get_as_str method?

        if nort_mon_id is None:
            await ctx.send(
                "You do not own a NortMon" if member is ctx.author else
                f"{member.display_name} does not own a NortMon"
            )
            return

        rarity, idx = nort_mon_id.split("-") # TODO: handle potentially invalid strings (search for all str.split calls)

        nort_mon_data = dict_get_as_list(self.nort_mons_data, rarity)[int(idx)]
        name = nort_mon_data.get("name")
        brief = nort_mon_data.get("brief")
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
            value=f"{brief}",
            inline=False
        )
        embed_reply.add_field(
            name="\u200b",
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
                nort_mon_name = nort_mons_by_rarity[rand_idx].get("name")
                # Returns: tuple (str, str)
                return (nort_mon_name, f"{rarity}-{rand_idx}")


def setup(bot):
    bot.add_cog(NortMonsCog(bot))
