import discord
from discord.ext import commands
from constant import TOKEN

extensions = (
    'auto_thread',
    'thread_manage',
)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('$'),
            intents=discord.Intents.all(),
        )

    async def setup_hook(self):
        for extension in extensions:
            await self.load_extension(f'extensions.{extension}')
        await self.tree.sync()


def main():
    MyBot().run(TOKEN)


if __name__ == '__main__':
    main()
