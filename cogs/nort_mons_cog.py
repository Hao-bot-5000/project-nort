import discord
from discord.ext        import commands

from random             import uniform, randint
from utils              import get_json_path, get_json_data, dict_get_as_list

from cogs.base_cog      import BaseCog
from custom_errors      import TooManyArgumentsError

class NortMonsCog(BaseCog, name="NortMons"):
    nort_mons_path = get_json_path("nort_mons")
    nort_mons_data = get_json_data(nort_mons_path)

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

        await ctx.send("hello2 :)")
        # TODO: show member's NortMon if they currently have one



    # Helper Methods #
    NORT_MON_WEIGHTS = { "legendary": 0.01, "rare": 0.04, "common": 0.2, "useless": 0.8 }

    def get_random_nort_mon(self):
        rand_weight = uniform(0, next(reversed(self.NORT_MON_WEIGHTS.values())))

        for rarity, weight in self.NORT_MON_WEIGHTS.items():
            if rand_weight <= weight:
                nort_mons_data_by_rarity = dict_get_as_list(self.nort_mons_data, rarity)
                rand_id = randint(0, len(nort_mons_data_by_rarity) - 1)
                return f"{rarity}:{rand_id}"


def setup(bot):
    bot.add_cog(NortMonsCog(bot))
