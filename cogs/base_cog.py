import discord
from discord.ext                import commands
from utils                      import get_json_data, get_json_path, set_json_data

class BaseCog(commands.Cog):
    data_path = get_json_path("data")
    data = get_json_data(data_path)
    img_404_url = "https://i.imgur.com/OMFiBp5.png"

    def __init__(self, bot):
        self.bot = bot

    def get_guild_data(self, guild, data=None, default=False):
        """
            Return the guild data stored inside ``data``. If ``data`` is not given,
            retrieve the data from the ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            data: :class:`dict, optional`
                the JSON object.
            default: :class:`boolean, optional`
                a truth value determining whether to insert a default value if the data
                does not exist.

            Returns
            -------
            guild_data: :class:`dict`
                a guild's data.
            
            Raises
            ------
            LookupError:
                the guild's data could not be found inside ``data``.
        """

        if data is None:
            data = self.data

        guild_id = str(guild.id)
        guild_data = data.setdefault(guild_id, {}) if default else data.get(guild_id, {})
        if not isinstance(guild_data, dict):
            raise LookupError(f"Could not get guild data for '{guild.id}'")

        return guild_data

    def get_member_list_data(self, guild, guild_data=None, default=False):
        """
            Return a list of member data stored inside ``guild_data``. If ``guild_data``
            is not given, retrieve the guild data from the ``data.json`` file.

            Parameters
            ----------
            guild: :class:`discord.Guild`
                a discord guild.
            guild_data: :class:`dict, optional`
                a guild's data.
            default: :class:`boolean, optional`
                a truth value determining whether to insert a default value if the data
                does not exist.

            Returns
            -------
            member_list_data: :class:`dict`
                the data of members in the guild.
            
            Raises
            ------
            LookupError:
                the member list data could not be found inside ``guild_data``.
        """

        if guild_data is None:
            guild_data = self.get_guild_data(guild, default=default)

        member_list_data = (
            guild_data.setdefault("yc_members", {}) if default
            else guild_data.get("yc_members", {})
        )
        if not isinstance(member_list_data, dict):
            raise LookupError(f"Could not get members list for '{guild.id}'")

        return member_list_data

    def get_member_data(self, guild, member, member_list_data=None, default=False):
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
            default: :class:`boolean, optional`
                a truth value determining whether to insert a default value if the data
                does not exist.

            Returns
            -------
            member_data: :class:`dict`
                a guild member's data.
            
            Raises
            ------
            LookupError:
                the guild member's data could not be found inside ``member_list_data``.
        """

        if member_list_data is None:
            member_list_data = self.get_member_list_data(guild, default=default)

        member_id = str(member.id)
        member_data = (
            member_list_data.setdefault(member_id, {}) if default
            else member_list_data.get(member_id, {})
        )
        if not isinstance(member_data, dict):
            raise LookupError(f"Could not get member data for '{guild.id}-{member.id}'")

        return member_data

    def register_member(self, guild, member, member_list_data=None):
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
            member_list_data = self.get_member_list_data(guild, default=True)

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

    def member_is_registered(self, guild, member, member_list_data=None):
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
            member_list_data = self.get_member_list_data(guild)

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
            discord.BadArgument:
                the input could not be converted to a positive integer.
        """

        try:
            value = int(input) if input is not None else default
            if value < 1: raise ValueError("'input' must be greater than 0")
            return value
        except ValueError:
            raise commands.BadArgument()
