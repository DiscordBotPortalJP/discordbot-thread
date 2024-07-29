import discord
from discord.ext import commands
from daug.utils.dpyexcept import excepter

CHANNEL_TARGET_IDS = [
    1202176071454171146,
    1183562309147308164,
    1184633761174917231,
    1235799317160394792,
    1235765465733922887,
    1233601809478848582,
    1266669053217476690,
]


class AutoThreadCog(commands.Cog):
    def __init__(self, bot: commands.Context):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id not in CHANNEL_TARGET_IDS:
            return
        await message.create_thread(name='コメント欄')
        # name = message.content[:40]
        # if len(message.content) > 40:
        #     name = name + '...'
        # await message.create_thread(name=name)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoThreadCog(bot))
