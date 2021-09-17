from commands.base_command  import BaseCommand
from utils                  import get_emoji, JSON_DATA_PATH, get_json_data, set_json_data

class Initiate(BaseCommand):

    def __init__(self):
        description = "Add yourself to the YashCoin event"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        guild_id = str(message.guild.id)
        author_id = str(message.author.id)

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

            reply = "Thank you for joining YashCoin" + get_emoji(":tm:") + " Incorporated!"
        else:
            reply = "You are already a member of YashCoin" + get_emoji(":tm:") + " Incorporated"

        await message.channel.send(reply)
