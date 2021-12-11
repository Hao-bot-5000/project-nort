import discord
from discord.ext        import commands

import asyncio
from datetime           import date

from utils              import (get_json_path, get_json_data, set_json_data,
                                dict_get_as_int, dict_get_as_list)

from cogs.base_cog      import BaseCog

class QuestsCog(BaseCog, name="Quests"):
    quests_data_path = get_json_path("quests")
    quests_data = get_json_data(quests_data_path)

    def __init__(self, bot):
        super().__init__(bot)

    ### Daily Claim Command ###
    @commands.command(
        brief="Claim 600 daily NortBucks",
        description="Claim 600 daily NortBucks every day (PT Time)"
    )
    @commands.guild_only()
    async def daily(self, ctx):
        member_data = self.get_member_data(ctx.guild, ctx.author, default=True)

        nort_bucks = dict_get_as_int(member_data, "nort_bucks", 0)
        prev_daily = member_data.get("prev_daily") # TODO: create dict_get_as_str method?

        today = str(date.today())
        if prev_daily != today:
            member_data["nort_bucks"] = nort_bucks + 600
            member_data["prev_daily"] = today

            await ctx.send("Daily NortBucks successfully claimed!")
        else:
            await ctx.send("Daily NortBucks already claimed!")

        set_json_data(self.data_path, self.data)

    ### Expedition Command ###
    @commands.command(
        aliases=["exp"],
        brief="Go on expedition to find NortBucks",
        description="Start an expedition based on the given level "
                    "(short, normal, long)"
    )
    @commands.guild_only()
    async def expedition(self, ctx, level: str=None):
        # Retrieve json contents
        member_data = self.get_member_data(ctx.guild, ctx.author, default=True)

        if member_data.get("on_expedition") == 0:
            await self.start_expedition(ctx, member_data, level)
        else:
            await ctx.send("Currently on expedition!")



    ### Helper Methods ###
    def get_quest_data(self, quest_name, quest_list_data=None):
        """
            Return the quest data stored inside ``quest_list_data``. If
            ``quest_list_data`` is not given, retrieve the quest list data from the
            ``quests.json`` file.

            Parameters
            ----------
            quest_name: :class:`str`
                the name of a quest.
            member_list_data: :class:`dict, optional`
                the data of every quest stored inside the JSON file.

            Returns
            -------
            quest_data: :class:`dict`
                a quest's data.
            
            Raises
            ------
            ValueError:
                the quest's data could not be found inside ``quest_list_data``.
        """

        if quest_list_data is None:
            quest_list_data = self.quests_data

        quest_data = quest_list_data.get(quest_name)
        if not isinstance(quest_data, dict):
            raise ValueError(f"Could not get quest data for '{quest_name}'")

        return quest_data

    async def start_expedition(self, ctx, member_data, level):
        """
            Start an expedition that lasts for a set duration based on the given level.
            If the expedition is successful, add to the member's balance a set amount
            of NortBucks and send a message through the context indicating that the
            expedition has completed. If any invalid inputs were given or the expedition
            data could not be retrieved, send an error message through the context.

            Parameters
            ----------
            ctx: :class:`discord.Context`
                the current context for a command sent by a member.
            member_data: :class:`dict`
                a member's data.
            level: :class:`str`
                the expedition's difficulty level.
        """

        quest_data = self.get_quest_data("expedition")
        num = dict_get_as_int(quest_data, "num_variations", 0)
        difficulties = dict_get_as_list(quest_data, "difficulty")
        durations = dict_get_as_list(quest_data, "duration")
        rewards = dict_get_as_list(quest_data, "reward")

        if num < 1 or not all(len(l) == num for l in (difficulties, durations, rewards)):
            await ctx.send("Failed to retrieve quest data...")
            return

        if level is None:
            level = difficulties[0]
        elif level not in difficulties:
            await ctx.send(f"Please input a valid level ({', '.join(difficulties)})")
            return

        member_data["on_expedition"] = 1
        set_json_data(self.data_path, self.data)
        await ctx.send("Expedition started!")

        idx = difficulties.index(level)
        await asyncio.sleep(durations[idx])

        nort_bucks = dict_get_as_int(member_data, "nort_bucks", 0)
        gain = rewards[idx]
        member_data["nort_bucks"] = nort_bucks + gain
        member_data["on_expedition"] = 0

        set_json_data(self.data_path, self.data)
        await ctx.send(
            f"{ctx.author.mention}\nYour expedition has completed, " +
            f"netting you `{gain}` NortBucks!"
        )


def setup(bot):
    bot.add_cog(QuestsCog(bot))
