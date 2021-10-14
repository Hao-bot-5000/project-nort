import discord
from discord.ext    import commands
from utils          import get_json_path, get_json_data, set_json_data

from custom_errors  import InvalidTypeError

class BaseCog(commands.Cog):
    def __init__(self, bot, category):
        self.bot = bot
        self.category = category

        self.data_path = get_json_path("data")

    # Get data from JSON file
    async def get_data(self):
        return await get_json_data(self.data_path)

    async def get_guild_data(self, guild, data=None):
        if data is None:
            data = await self.get_data()

        guild_data = data.setdefault(str(guild.id), {})
        if not isinstance(guild_data, dict):
            raise ValueError(f"Could not get guild data for '{guild.id}'")

        return guild_data

    async def get_member_list_data(self, guild, guild_data=None):
        if guild_data is None:
            guild_data = await self.get_guild_data(guild)

        member_list_data = guild_data.setdefault("yc_members", {})
        if not isinstance(member_list_data, dict):
            raise ValueError(f"Could not get members list for '{guild.id}'")

        return member_list_data

    async def get_member_data(self, guild, member, member_list_data=None):
        if member_list_data is None:
            member_list_data = await self.get_member_list_data(guild)

        member_data = member_list_data.setdefault(str(member.id), {})
        if not isinstance(member_data, dict):
            raise ValueError(f"Could not get member data for '{guild.id}-{member.id}'")

        return member_data

    # Returns true if successfully registered member, false otherwise
    async def register_member(self, guild, member, member_list_data=None):
        if member_list_data is None:
            member_list_data = await self.get_member_list_data(guild)

        is_new_member = not self.member_is_registered(guild, member, member_list_data)
        if is_new_member:
            member_list_data[member.id] = {
                "nort_bucks"    : 0,
                "yash_coins"    : 0,
                "cringe_meter"  : 0,
                "prev_daily"    : None,
                "on_expedition" : 0
            }

        return is_new_member

    async def member_is_registered(self, guild, member, member_list_data=None):
        if member_list_data is None:
            member_list_data = await self.get_member_list_data(guild)

        return member_list_data.get(str(member.id)) is not None

    async def add_reactions(self, message, *emojis):
        for emoji in emojis:
            await message.add_reaction(emoji)  

    @staticmethod
    def create_embed():
        return discord.Embed(color=0x010101)

    @staticmethod
    def input_to_positive_int(input, default=1):
        value = int(input) if input is not None else default
        if value < 1: raise InvalidTypeError("positive integer")

        return value