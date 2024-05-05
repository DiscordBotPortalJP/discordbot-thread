import traceback
import discord
from discord import app_commands
from discord.ext import commands
from utils import extract_mentions
from utils import extract_role_mentions
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger
from daug.constants import COLOUR_EMBED_GRAY
from typing import Optional


MESSAGE_CREATE_THREAD = 'ここでメンションをすると新しいメンバーを招待できます'
EMBED_CREATE_THREAD = discord.Embed(
    description='デフォルトの設定は\n・1日間発言がなかったら自動でクローズ(非表示に)\n・メンション時に招待するかを確認する',
    colour=COLOUR_EMBED_GRAY,
)


async def create_private_thread_with_voice(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.voice is None:
        await interaction.followup.send('VCに上がってから試してください', ephemeral=True)
        return
    thread = await interaction.channel.create_thread(
        name=interaction.user.voice.channel.name,
        auto_archive_duration=60*24*1,
        type=None,
        invitable=False,
    )
    try:
        mentions = ' '.join([m.mention for m in interaction.user.voice.channel.members])
        await thread.send(f'いらっしゃい！ {mentions}')
    except discord.errors.Forbidden:
        await interaction.followup.send('スレッドにユーザーを追加する権限がありません', ephemeral=True)
        return
    except discord.errors.HTTPException:
        await interaction.followup.send('招待に失敗しました', ephemeral=True)
        return
    await thread.send(f'{interaction.user.mention} {MESSAGE_CREATE_THREAD}', embed=EMBED_CREATE_THREAD, view=ThreadManageButtons())
    message = f'プライベートスレッドを作成したよ {thread.mention}'
    await interaction.followup.send(message, ephemeral=True)


class ChangeNameModal(discord.ui.Modal, title='スレッドの名前を変更する'):
    def __init__(self):
        super().__init__()

    thread_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label='スレッド名',
        required=True,
    )

    @excepter
    @dpylogger
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.edit(name=self.thread_name.value)
        except discord.errors.Forbidden:
            await interaction.followup.send('スレッドを編集する権限がありません', ephemeral=True)
            return
        except discord.errors.HTTPException:
            await interaction.followup.send('スレッドの編集に失敗しました', ephemeral=True)
            return

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send('エラーが発生しました', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class CreatePrivateThreadModal(discord.ui.Modal, title='プライベートスレッドを作成する'):
    def __init__(self):
        super().__init__()

    thread_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label='スレッド名',
        required=True,
    )

    @excepter
    @dpylogger
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thread = await interaction.channel.create_thread(
            name=self.thread_name.value,
            auto_archive_duration=60*24*7,
            type=None,
            invitable=False,
        )
        await thread.send(f'{interaction.user.mention}{MESSAGE_CREATE_THREAD}', view=ThreadManageButtons())
        message = f'プライベートスレッドを作成しました {thread.mention}'
        await interaction.followup.send(message, ephemeral=True)
        try:
            await thread.add_user(interaction.user)
        except discord.errors.Forbidden:
            await interaction.followup.send('スレッドにユーザーを追加する権限がありません', ephemeral=True)
            return
        except discord.errors.HTTPException:
            await interaction.followup.send('招待に失敗しました', ephemeral=True)
            return

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send('エラーが発生しました', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class CreatePrivateThreadButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @excepter
    @dpylogger
    @discord.ui.button(label='通常作成', style=discord.ButtonStyle.green, custom_id='thread:create:private:default')
    async def _create_private_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreatePrivateThreadModal())

    @excepter
    @dpylogger
    @discord.ui.button(label='現在のVC用に作成', style=discord.ButtonStyle.green, custom_id='thread:create:private:voice')
    async def _create_private_thread_with_voice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_private_thread_with_voice(interaction)


class ThreadManageButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッド名変更', row=0, style=discord.ButtonStyle.green, custom_id='thread:change_name')
    async def _change_thread_name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeNameModal())

    @excepter
    @dpylogger
    @discord.ui.button(label='VCとメンバーを同期', row=0, style=discord.ButtonStyle.green, custom_id='thread:invite_voice')
    async def _invite_voice_members_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice is None:
            await interaction.followup.send('VCに上がってから試してください', ephemeral=True)
            return
        thread_members = await interaction.channel.fetch_members()
        voice_members = interaction.user.voice.channel.members
        for thread_member in thread_members:
            if thread_member.id not in [m.id for m in voice_members]:
                try:
                    await interaction.channel.remove_user(thread_member)
                except discord.errors.Forbidden:
                    await interaction.followup.send('スレッドからユーザーを退出させる権限がありません', ephemeral=True)
                except discord.errors.HTTPException:
                    await interaction.followup.send('退出させるのに失敗しました', ephemeral=True)
        for voice_member in voice_members:
            if voice_member.id not in [m.id for m in thread_members]:
                try:
                    await interaction.channel.add_user(voice_member)
                except discord.errors.Forbidden:
                    await interaction.followup.send('スレッドにユーザーを招待する権限がありません', ephemeral=True)
                except discord.errors.HTTPException:
                    await interaction.followup.send('招待に失敗しました', ephemeral=True)

    @excepter
    @dpylogger
    @discord.ui.button(label='期限を1日に', row=1, style=discord.ButtonStyle.green, custom_id='thread:archive_duration_1day')
    async def _archive_duration_1day_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.channel.edit(auto_archive_duration=60*24*1)
        await interaction.followup.send('1日間発言がなかったら自動でクローズする設定に変更しました')

    @excepter
    @dpylogger
    @discord.ui.button(label='期限を1週間に', row=1, style=discord.ButtonStyle.green, custom_id='thread:archive_duration_1week')
    async def _archive_duration_1week_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.channel.edit(auto_archive_duration=60*24*7)
        await interaction.followup.send('1週間発言がなかったら自動でクローズする設定に変更しました')

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドを退出', row=1, style=discord.ButtonStyle.gray, custom_id='thread:leave')
    async def _leave_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('本当にこのスレッドを退出しますか？', view=ConfirmLeaveThreadButton(), ephemeral=True)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドをクローズ', row=1, style=discord.ButtonStyle.gray, custom_id='thread:close')
    async def _close_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('本当にこのスレッドをクローズしますか？', view=ConfirmCloseThreadButton(), ephemeral=True)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドを削除', row=1, style=discord.ButtonStyle.red, custom_id='thread:delete')
    async def _delete_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('本当にこのスレッドを削除しますか？', view=ConfirmDeleteThreadButton(), ephemeral=True)


class ConfirmLeaveThreadButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドを退出する', style=discord.ButtonStyle.red)
    async def _leave_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.remove_user(interaction.user)
        except discord.errors.Forbidden:
            await interaction.followup.send('スレッドからユーザーを退出させる権限がありません', ephemeral=True)
        except discord.errors.HTTPException:
            await interaction.followup.send('退出させるのに失敗しました', ephemeral=True)


class ConfirmCloseThreadButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドをクローズする', style=discord.ButtonStyle.red)
    async def _close_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.edit(archived=True)
        except discord.errors.Forbidden:
            await interaction.followup.send('スレッドを編集する権限がありません', ephemeral=True)
        except discord.errors.HTTPException:
            await interaction.followup.send('スレッドのクローズに失敗しました', ephemeral=True)


class ConfirmDeleteThreadButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @excepter
    @dpylogger
    @discord.ui.button(label='スレッドを削除する', style=discord.ButtonStyle.red)
    async def _delete_thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.delete()
        except discord.errors.Forbidden:
            await interaction.followup.send('スレッドを削除する権限がありません', ephemeral=True)
        except discord.errors.HTTPException:
            await interaction.followup.send('スレッドの削除に失敗しました', ephemeral=True)


class ThreadManageCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(CreatePrivateThreadButtons())
        self.bot.add_view(ThreadManageButtons())

    @app_commands.command(name='プライベートスレッド作成ボタン', description='プライベートスレッドを作成できるボタンを設置します')
    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def _secret_post_button_app_command(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.manage_channels:
            await interaction.response.send_message('チャンネル管理権限が必要です', ephemeral=True)
            return
        if not interaction.channel.type is discord.ChannelType.text:
            await interaction.response.send_message('テキストチャンネルのみボタンを設置できます', ephemeral=True)
            return
        await interaction.response.send_message('誰でもプライベートスレッドを作成できるボタンです。', ephemeral=True)
        await interaction.channel.send(
            'ボタンを押すとプライベートスレッドを作成します',
            view=CreatePrivateThreadButtons(),
        )

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.author.system:
            return
        if message.guild is None:
            return
        if message.channel.type is discord.ChannelType.private_thread:
            if message.channel.owner != self.bot.user:
                return
            if message.content in ['メニュー', 'ボタン', 'メニュー']:
                await message.channel.send(view=ThreadManageButtons())
                return
            view = discord.ui.View()
            button = discord.ui.Button(style=discord.ButtonStyle.green, label='追加する', custom_id='thread:invite_member')
            view.add_item(button)
            button = discord.ui.Button(style=discord.ButtonStyle.red, label='追加しない', custom_id='message_delete')
            view.add_item(button)
            thread_members = await message.channel.fetch_members()
            for member in message.mentions:
                if member.id in [m.id for m in thread_members]:
                    continue
                embed = discord.Embed(
                    description=f'{member.mention} をこのスレッドに追加しますか？',
                    colour=COLOUR_EMBED_GRAY,
                )
                await message.channel.send(embed=embed, view=view)
            for role in message.role_mentions:
                embed = discord.Embed(
                    description=f'{role.mention} をこのスレッドに追加しますか？',
                    colour=COLOUR_EMBED_GRAY,
                )
                await message.channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    @excepter
    async def on_interaction(self, interaction: discord.Interaction):
        custom_id: Optional[str] = interaction.data.get('custom_id')
        if custom_id is None:
            return
        if custom_id == 'message_delete':
            await interaction.message.delete()
            return
        if custom_id == 'thread:invite_member':
            members = extract_mentions(interaction.guild, interaction.message.embeds[0].description)
            roles = extract_role_mentions(interaction.guild, interaction.message.embeds[0].description)
            try:
                for member in members:
                    if member is None:
                        continue
                    await interaction.channel.send(f'{member.mention} を招待しました')
                    await interaction.channel.add_user(member)
                for role in roles:
                    if role is None:
                        continue
                    await interaction.channel.send(f'{role.mention} を招待しました')
                    for member in role.members:
                        await interaction.channel.add_user(member)
            except discord.errors.Forbidden:
                await interaction.response.send_message('スレッドにユーザーを招待する権限がありません', ephemeral=True)
                return
            except discord.errors.HTTPException:
                await interaction.response.send_message('招待に失敗しました', ephemeral=True)
                return
            await interaction.message.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ThreadManageCog(bot))
