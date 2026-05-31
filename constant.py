import discord
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')
OPS_LOG_HUB_URL = getenv('OPS_LOG_HUB_URL')
OPS_LOG_HUB_KEY = getenv('OPS_LOG_HUB_KEY')
OPS_LOG_PROJECT = getenv('OPS_LOG_PROJECT', 'discordbot-thread')
OPS_LOG_ENVIRONMENT = getenv('OPS_LOG_ENVIRONMENT', 'development')
CHANNEL_LOG_SYSTEM_ID = 1193579117552087090
CHANNEL_LOG_TRACEBACK_ID = 1193579117552087090
COLOUR_EMBED_GRAY = discord.Colour.from_rgb(43, 45, 49)
