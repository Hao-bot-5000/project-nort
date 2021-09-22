import discord
from discord.ext        import commands

from cogs.base_command  import BaseCommand

from utils              import (JSON_DATA_PATH, get_json_data, set_json_data, 
                                get_emoji, get_mentioned_member, create_progress_bar)


class YashCoinCommands(BaseCommand):
    def __init__(self, bot):
        super().__init__(bot)
    
    ### Initiate command ###
    @commands.command(
        name="initiate", 
        brief="Enters YashCoin event", 
        description="Adds yourself to the YashCoin event"
    )
    @commands.guild_only()
    async def initiate(self, ctx):
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
        name="balance", 
        brief="Displays balance", 
        description="Displays the member's current balance"
    )
    @commands.guild_only()
    async def balance(self, ctx, *args):
        member = await self.__get_yc_member(ctx, args)

        if member is None:
            return # Error messages are handled inside the private func

        nortcoins = member.get("data", { "nort_coins" : 0 }).get("nort_coins")
        yashcoins = member.get("data", { "yash_coins" : 0 }).get("yash_coins")

        balance_description = (
            f"{get_emoji(':coin:')} `NortCoins: {nortcoins}`\n" + 
            f"{get_emoji(':moneybag:')} `YashCoins: {yashcoins}`"
        )

        embed_reply = discord.Embed(
            color=discord.Color.green(),
            title=f"{member.get('display_name', 'Member')}'s Balance:",
            description=balance_description
        )

        await ctx.send(embed=embed_reply)

    ### CM Command ###
    @commands.command(
        name="cringemeter", 
        brief="Displays cringe meter", 
        description="Displays the member's cringe meter"
    )
    @commands.guild_only()
    async def cringemeter(self, ctx, *args):
        member = await self.__get_yc_member(ctx, args)

        if member is None:
            return # Error messages are handled inside the private func

        cringe_meter_value = member.get("data", { "cringe_meter" : 0 }).get("cringe_meter")
        cringe_meter_display = await create_progress_bar(cringe_meter_value)
        reply = f"{cringe_meter_display}"

        await ctx.send(reply)



    ### Private methods ###
    # Returns None if member cannot be found in the guild
    # Returns None if member is found in the guild, but not in the JSON file
    # Returns a dict containing the member's data and display name if member is found
    async def __get_yc_member(self, ctx, args):
        num_params = len(args)
        guild = ctx.guild
        guild_id = str(guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, None)
        yc_members_data = guild_data.get("yc_members", None) if guild_data else None

        if num_params == 0:
            member = ctx.author
        elif num_params == 1:
            member = await get_mentioned_member(ctx.message, backup=args[0])
        else:
            await ctx.send("Too many arguments")
            return None
        
        if member is None:
            await ctx.send(f"Member {args[0]} could not be found")
            return None

        member_id = str(member.id)
        member_data = yc_members_data.get(member_id, None) if yc_members_data else None

        if member_data is None:
            await ctx.send(
                (f"{member.display_name} is " if member != ctx.author else "You are ") + 
                f"not a member of YashCoin{get_emoji(':tm:')} Incorporated"
            )
            return None
        
        return { "data" : member_data, "display_name" : member.display_name }


def setup(bot):
    bot.add_cog(YashCoinCommands(bot)) 
