import os
from dotenv  import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



# The prefix that will be used to parse commands.
# It doesn't have to be a single character!
COMMAND_PREFIX = "!nort "

# The bot token. Keep this secret!
BOT_TOKEN = TOKEN

# The now playing game. Set this to anything false-y ("", None) to disable it
NOW_PLAYING = "FF14 with the Norters" # COMMAND_PREFIX + "commands"

# Base directory. Feel free to use it if you want.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
