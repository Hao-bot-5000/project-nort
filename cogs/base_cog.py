import discord
from discord.ext    import commands
from utils          import get_json_path, get_json_data, set_json_data

from custom_errors  import InvalidTypeError

class BaseCog(commands.Cog):
    def __init__(self, bot, category):
        self.bot = bot
        self.category = category

        self.data_path = get_json_path("data")

    async def get_data(self):
        """
            Return the data stored inside the ``data.json`` file.

            Returns
            -------
            json_data: :class:`dict`
                the JSON object.
        """

        return await get_json_data(self.data_path)

    async def get_guild_data(self, guild, data=None):
        """
            Return the guild data stored inside ``data``. If ``data`` is not given,
            retrieve the data from the ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            data: :class:`dict, optional`
                the JSON object.

            Returns
            -------
            guild_data: :class:`dict`
                a guild's data.
            
            Raises
            ------
            ValueError:
                the guild's data could not be found inside ``data``.
        """

        if data is None:
            data = await self.get_data()

        guild_data = data.setdefault(str(guild.id), {})
        if not isinstance(guild_data, dict):
            raise ValueError(f"Could not get guild data for '{guild.id}'")

        return guild_data

    async def get_member_list_data(self, guild, guild_data=None):
        """
            Return a list of member data stored inside ``guild_data``. If ``guild_data``
            is not given, retrieve the guild data from the ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            guild_data: :class:`dict, optional`
                a guild's data.

            Returns
            -------
            member_list_data: :class:`dict`
                the data of members in the guild.
            
            Raises
            ------
            ValueError:
                the member list data could not be found inside ``guild_data``.
        """

        if guild_data is None:
            guild_data = await self.get_guild_data(guild)

        member_list_data = guild_data.setdefault("yc_members", {})
        if not isinstance(member_list_data, dict):
            raise ValueError(f"Could not get members list for '{guild.id}'")

        return member_list_data

    async def get_member_data(self, guild, member, member_list_data=None):
        """
            Return the guild member data stored inside ``member_list_data``. If
            ``member_list_data`` is not given, retrieve the member list data from the
            ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            member: :class:`discord.Member`
                a discord member that is part of the guild.
            member_list_data: :class:`dict, optional`
                the data of members in the guild.

            Returns
            -------
            member_data: :class:`dict`
                a guild member's data.
            
            Raises
            ------
            ValueError:
                the guild member's data could not be found inside ``member_list_data``.
        """

        if member_list_data is None:
            member_list_data = await self.get_member_list_data(guild)

        member_data = member_list_data.setdefault(str(member.id), {})
        if not isinstance(member_data, dict):
            raise ValueError(f"Could not get member data for '{guild.id}-{member.id}'")

        return member_data

    async def register_member(self, guild, member, member_list_data=None):
        """
            Store the new guild member data into the ``data.json`` file. Return ``True``
            if the guild member was successfully registered, and ``False`` otherwise.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            member: :class:`discord.Member`
                a discord member that is part of the guild.
            member_list_data: :class:`dict, optional`
                the data of members in the guild.

            Returns
            -------
            is_new_member: :class:`boolean`
                a value indicating whether the member was successfully registered.
        """

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
        """
            Return ``True`` if the guild member data exists in ``member_list_data``, and
            ``False`` otherwise. If ``member_list_data`` is not given, retrieve the
            member list data from the ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            member: :class:`discord.Member`
                a discord member that is part of the guild.
            member_list_data: :class:`dict, optional`
                the data of members in the guild.

            Returns
            -------
            is_registered: :class:`boolean`
                a value indicating whether the member is currently registered.
        """

        if member_list_data is None:
            member_list_data = await self.get_member_list_data(guild)

        return member_list_data.get(str(member.id)) is not None

    async def add_reactions(self, message, *emojis):
        """
            Add reactions based on the emojis given (the bot must have permissions to
            react to messages).

            Parameters
            ----------
            message: :class:`discord.Message`
                a discord message.
            *emojis:
                the emojis to add onto the message.
        """

        for emoji in emojis:
            await message.add_reaction(emoji)  

    @staticmethod
    def create_embed():
        """
            Return an embed object.

            Returns
            -------
            embed: :class:`discord.Embed`
                a nearly-black color-coded embed.
        """

        # 'black' is used by Discord to handle color themes
        return discord.Embed(color=0x010101)

    @staticmethod
    def input_to_positive_int(input=None, default=1):
        """
            Return a positive integer based on the input value. If ``input`` is not
            given, return ``default``.

            Parameters
            ----------
            input: :class:`Any, optional`
                an input value.
            default: :class:`int, optional`
                a default integer value.
            
            Returns
            -------
            value: :class:`int`
                a positive integer representation of ``input``.
            
            Raises
            ------
            InvalidTypeError:
                the input could not be converted to a positive integer.
        """
        value = int(input) if input is not None else default
        # NOTE: Do I really need to raise a custom error, or can I just raise ValueError?
        if value < 1: raise InvalidTypeError("positive integer")

        return value