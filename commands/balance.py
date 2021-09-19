from discord                import Color, Embed

from commands.base_command  import BaseCommand
from utils                  import get_emoji, JSON_DATA_PATH, get_json_data, get_mentioned_member

class Balance(BaseCommand):

    def __init__(self):
        description = "Displays the member's balance"
        params = ["member"]
        super().__init__(description, params)

    async def handle(self, params, message, client):
        num_params = len(params)
        guild = message.guild
        guild_id = str(guild.id)

        # Retrieve json contents
        json_data = await get_json_data(JSON_DATA_PATH)
        guild_data = json_data.get(guild_id, None)
        yc_members_data = guild_data.get("yc_members", None) if guild_data else None

        if num_params == 0:
            member = message.author
        elif num_params == 1:
            member = await get_mentioned_member(message, backup=params[0])
        else:
            await message.channel.send("Too many arguments")
            return
        
        if member is None:
            await message.channel.send(f"Member {params[0]} could not be found")
            return

        member_id = str(member.id)
        member_data = yc_members_data.get(member_id, None) if yc_members_data else None

        if member_data is None:
            await message.channel.send(
                f"{member.display_name} is not a member of YashCoin" + 
                get_emoji(":tm:") + " Incorporated"
            )
            return

        nortcoins = member_data.get("yashcoins", 0)
        yashcoins = member_data.get("yashcoins", 0)

        balance_description = (
            get_emoji(":coin:")     + f" `NortCoins: {nortcoins}`\n" + 
            get_emoji(":moneybag:") + f" `YashCoins: {yashcoins}`"
        )

        embed_reply = Embed(
            color=Color.green(),
            title=f"{member.display_name}'s Balance:",
            description=balance_description
        )

        await message.channel.send(embed=embed_reply)
