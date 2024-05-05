import discord
from discord.ext import commands
from constant import TOKEN

extensions = (
    'auto_thread',
)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='$',
            help_command=None,
            intents=discord.Intents.all(),
        )

    async def setup_hook(self):
        for extension in extensions:
            await self.load_extension(f'extensions.{extension}')
        # GUILD_ID = 1139109855001583676
        # await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        # await self.tree.sync()


def main():
    MyBot().run(TOKEN)


if __name__ == '__main__':
    main()
