import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from utils              import (JSON_DATA_PATH, get_json_data, set_json_data, 
                                get_emoji, get_mentioned_member, create_progress_bar, 
                                create_black_embed)

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
            await ctx.send("Too many arguments")
            return

        guild_id = str(ctx.guild.id)
        author_id = str(ctx.author.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, { "yc_members" : {} })
        yc_members_data = guild_data.get("yc_members")

        # Update contents of json file if author id does not yet exist
        if author_id not in yc_members_data:
            yc_members_data[author_id] = {
                "nort_coins" : 0,
                "yash_coins" : 0,
                "cringe_meter" : 0
            }
            guild_data.update({ "yc_members" : yc_members_data })
            json_data.update({ guild_id : guild_data })

            await set_json_data(JSON_DATA_PATH, json_data)

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
        member = await self.__get_yc_member(ctx, member if member else ctx.author, args)

        if member is None:
            return # Error messages are handled inside the private func

        nortcoins = member.get("data", {}).get("nort_coins", 0)
        yashcoins = member.get("data", {}).get("yash_coins", 0)

        embed_reply = create_black_embed()

        embed_reply.set_author(
            name=f"{member.get('display_name', 'Member')}'s Balance:", 
            icon_url=member.get("icon", None)
        )
        embed_reply.add_field(
            name="\u200b", 
            value=(f"{get_emoji(':moneybag:')} **YashCoins**\n" + 
                   f"{get_emoji(':coin:')} **NortCoins**"), 
            inline=True
        )
        embed_reply.add_field(
            name="\u200b", 
            value=(f"`{yashcoins}`\n" + 
                   f"`{nortcoins}`"), 
            inline=True
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
        member = await self.__get_yc_member(ctx, member if member else ctx.author, args)

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
        embed_reply.add_field(
            name="\u200b", 
            value=("**Status**\n" + 
                   f"**{cringe_meter_bar[0]}%**"), 
            inline=True
        )
        embed_reply.add_field(
            name="\u200b", 
            value=(f"`{cringe_meter_status}`\n" + 
                   f"`{cringe_meter_bar[1]}`"), 
            inline=True
        )

        await ctx.send(embed=embed_reply)



    ### Private methods ###
    # Returns None if member cannot be found in the guild
    # Returns None if member is found in the guild, but not in the JSON file
    # Returns a dict containing the member's data and display name if member is found
    async def __get_yc_member(self, ctx, member, args):
        if len(args) > 0:
            await ctx.send("Too many arguments")
            return None

        guild_id = str(ctx.guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
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

        if member_data is None:
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
    
    __CRINGE_STATUSES = ["Not Cringe", "Kinda Cringe", "Cringe", "Ultra Cringe", "YASH"]
    def __get_cringe_status(self, percent):
        if percent == 0.69: return "Nice"
        return self.__CRINGE_STATUSES[int(percent * (len(self.__CRINGE_STATUSES) - 1))]


def setup(bot):
    bot.add_cog(YashCoinCog(bot)) 
