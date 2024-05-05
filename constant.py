import discord
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')
CHANNEL_LOG_SYSTEM_ID = 1193579117552087090
CHANNEL_LOG_TRACEBACK_ID = 1193579117552087090
COLOUR_EMBED_GRAY = discord.Colour.from_rgb(43, 45, 49)
