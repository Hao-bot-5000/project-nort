from os.path    import join
from os         import remove

import json
import math

from emoji      import emojize

import discord
import settings

# Returns a path relative to the bot directory
def get_rel_path(rel_path):
    return join(settings.BASE_DIR, rel_path)


# Returns an emoji as required to send it in a message
# You can pass the emoji name with or without colons
# If fail_silently is True, it will not raise an exception
# if the emoji is not found, it will return the input instead
def get_emoji(emoji_name, fail_silently=False):
    alias = emoji_name if emoji_name[0] == emoji_name[-1] == ":" \
            else f":{emoji_name}:"
    the_emoji = emojize(alias, use_aliases=True)

    if the_emoji == alias and not fail_silently:
        raise ValueError(f"Emoji {alias} not found!")

    return the_emoji


# A shortcut to get a channel by a certain attribute
# Uses the channel name by default
# If many matching channels are found, returns the first one
def get_channel(bot, value, attribute="name"):
    channel = next((c for c in bot.get_all_channels() 
                    if getattr(c, attribute).lower() == value.lower()), None)
    if not channel:
        raise ValueError("No such channel")
    return channel


# Shortcut method to send a message in a channel with a certain name
# You can pass more positional arguments to send_message
# Uses get_channel, so you should be sure that the bot has access to only
# one channel with such name
async def send_in_channel(bot, channel_name, *args):
    await get_channel(bot, channel_name).send(*args)


# Attempts to upload a file in a certain channel
# content refers to the additional text that can be sent alongside the file
# delete_after_send can be set to True to delete the file afterwards
async def try_upload_file(bot, channel, file_path, content=None, 
                          delete_after_send=False, retries=3):
    used_retries = 0
    sent_msg = None

    while not sent_msg and used_retries < retries:
        try:
            sent_msg = await bot.send_file(channel, file_path,
                                              content=content)
        except discord.HTTPException:
            used_retries += 1

    if delete_after_send:
        remove(file_path)

    if not sent_msg:
        await channel.send("Oops, something happened. Please try again.")

    return sent_msg



### JSON Helpers ###
JSON_DATA_PATH = "./assets/json/data.json"

# Retrieve json contents based on path URL
# If file is not a valid JSON document, return an empty dictionary
# If file cannot be opened, throws an error
async def get_json_data(path):
    try:
        json_file = open(path, "r")
        json_data = json.load(json_file)
    except json.JSONDecodeError:
        json_data = {}
    
    json_file.close()
    return json_data

# Modify json contents stored at path URL
# If file cannot be opened, throws an error
async def set_json_data(path, json_data):
    json_file = open(path, "w")
    json.dump(json_data, json_file, indent=4)
    json_file.close()



### Member Searching Helpers ###
# Attempts to retrieve a member based on the message's mention
# If no member is mentioned in the message, run a name-based and 
# id-based search to retrieve the member
# If the member cannot be found, returns None
async def get_mentioned_member(message, backup):
    guild = message.guild
    mentions = message.mentions

    member = mentions[0] if mentions else guild.get_member_named(backup)
    if not member:
        try:
            member = await guild.get_member(int(backup))
        except Exception:
            pass
    
    return member



### ETC ###
NUM_BARS = 25

# Returns a 2-tuple containing the percentage number and the progress bar
# If the input is not a number, raise an error
def create_progress_bar(percentage):
    if not isinstance(percentage, (int, float)):
        raise TypeError("input must be a number")

    percentage = min(1, max(0, percentage))

    bars = "\u25a0" * math.floor(percentage * NUM_BARS) + " " * math.ceil((1 - percentage) * NUM_BARS)
    return (int(percentage * 100), f"[{bars}]")

# Returns an Embed object with a black bar
def create_black_embed():
    return discord.Embed(color=0x010101)