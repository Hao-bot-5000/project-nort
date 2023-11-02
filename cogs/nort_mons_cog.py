from random                     import randint, uniform

import discord
from discord.ext                import commands
from utils                      import (dict_get_as_int, dict_get_as_list,
                                        get_json_data, get_json_path, set_json_data)

from cogs.base_cog              import BaseCog

class NortMonsCog(BaseCog, name="NortMons"):
    nort_mons_data_path = get_json_path("nort_mons")
    nort_mons_data = get_json_data(nort_mons_data_path)

    NORT_MON_COST = 400

    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(
        brief="Catch NortMon",
        description="Use your NortBucks to catch yourself a Nortmon of a random rarity "
                    "from the wild",
        ignore_extra=False
    )
    @commands.guild_only()
    async def catch(self, ctx):
        member_data = self.get_member_data(ctx.guild, ctx.author, default=True)
        member_nort_mon = member_data.get("nort_mon")

        if member_nort_mon is not None:
            await ctx.send("You already own a NortMon")
            return

        nort_bucks = dict_get_as_int(member_data, "nort_bucks")

        if nort_bucks < self.NORT_MON_COST:
            await ctx.send(
                f"You do not have the required `{self.NORT_MON_COST}` NortBucks to " +
                "spend on catching a NortMon"
            )
            return

        nort_mon_name, nort_mon_id = self.get_random_nort_mon()
        rarity, _ = nort_mon_id.split("-")

        member_data["nort_mon"] = nort_mon_id
        member_data["nort_bucks"] = nort_bucks - self.NORT_MON_COST
        set_json_data(self.data_path, self.data)

        await ctx.send(
            f"You've spent `{self.NORT_MON_COST}` NortBucks to catch " +
            f"**{nort_mon_name}** — a `{rarity.capitalize()}` NortMon!"
        )

    @commands.command(
        brief="Release NortMon",
        description="Release your current NortMon into the wild",
        ignore_extra=False
    )
    @commands.guild_only()
    async def release(self, ctx):
        member_data = self.get_member_data(ctx.guild, ctx.author)
        member_nort_mon = member_data.get("nort_mon")

        if member_nort_mon is None:
            await ctx.send("You do not own a NortMon")
            return

        member_data["nort_mon"] = None
        set_json_data(self.data_path, self.data)

        rarity, idx = member_nort_mon.split("-")
        nort_mon_data = dict_get_as_list(self.nort_mons_data, rarity)[int(idx)]
        nort_mon_name = nort_mon_data.get("name")

        await ctx.send(
            f"You've released your `{rarity.capitalize()}` **{nort_mon_name}**"
        )

    @commands.command(
        brief="Display NortMon",
        description="Display a member's current NortMon",
        ignore_extra=False
    )
    @commands.guild_only()
    async def nortmon(self, ctx, *, member: discord.Member=None):
        if member is None:
            member= ctx.author

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
        image_url = nort_mon_data.get("image") or self.img_404_url

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
    NORT_MON_WEIGHTS = { "legendary": 0.02, "rare": 0.08, "common": 0.5, "useless": 1 }

    def get_random_nort_mon(self):
        """
            Return a randomly selected NortMon.

            Returns
            -------
            nort_mon: :class:`tuple(str, str)`
                a tuple of size 2 containing the NortMon's name and id.
        """
        rand_weight = uniform(0, next(reversed(self.NORT_MON_WEIGHTS.values())))

        for rarity, weight in self.NORT_MON_WEIGHTS.items():
            if rand_weight <= weight:
                nort_mons_by_rarity = dict_get_as_list(self.nort_mons_data, rarity)
                rand_idx = randint(0, len(nort_mons_by_rarity) - 1)
                nort_mon_name = nort_mons_by_rarity[rand_idx].get("name")
                # Returns: tuple (str, str)
                return (nort_mon_name, f"{rarity}-{rand_idx}")


async def setup(bot):
    await bot.add_cog(NortMonsCog(bot))
