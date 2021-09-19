from commands.base_command  import BaseCommand
from utils                  import get_emoji, JSON_DATA_PATH, get_json_data, get_mentioned_member, create_progress_bar

class Cm(BaseCommand):

    def __init__(self):
        description = "Displays the member's cringe meter"
        params = ["member"]
        super().__init__(description, params)

    async def handle(self, params, message, client):
        num_params = len(params)
        guild_id = str(message.guild.id)

        # Retrieve json contents
        # NOTE: 20+ duplicate lines of code between cringemeter.py and balance.py,
        #       is it worth converting this block of code into a helper function?
        #       i.e. get_value_from_dict(type="member", dict=yc_members_data, count=1)
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
            await message.channel.send(f"{member.display_name} is not a member of YashCoin" + get_emoji(":tm:") + " Incorporated")
            return

        cringe_meter_value = member_data.get("cringe_meter", 0)
        cringe_meter_display = await create_progress_bar(cringe_meter_value)
        reply = f"{cringe_meter_display}"

        await message.channel.send(reply)
