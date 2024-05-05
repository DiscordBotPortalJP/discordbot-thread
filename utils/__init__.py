import re
import discord


def extract_mentions(guild: discord.Guild, text: str) -> list[discord.Member]:
    return [guild.get_member(int(x)) for x in re.findall(r'<@!?([0-9]{15,20})>', text)]


def extract_role_mentions(guild: discord.Guild, text: str) -> list[discord.Role]:
    return [guild.get_role(int(x)) for x in re.findall(r'<@&([0-9]{15,20})>', text)]
