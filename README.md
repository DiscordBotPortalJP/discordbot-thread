# discordbot-thread

スレッド作成、プライベートスレッド運用、メンバー招待補助を行う Discord Bot です。

## 主な機能

- 指定チャンネルの投稿から自動でコメント用スレッドを作成します
- `/プライベートスレッド作成ボタン` で、誰でもプライベートスレッドを作れるボタンを設置します
- スレッド名変更、VCメンバー同期、アーカイブ期間変更、退出、クローズ、削除をボタンで操作できます
- プライベートスレッド内でメンションされたユーザーやロールの招待確認を出します

## 必要な設定

```env
DISCORD_BOT_TOKEN=
OPS_LOG_HUB_URL=
OPS_LOG_HUB_KEY=
OPS_LOG_PROJECT=discordbot-thread
OPS_LOG_ENVIRONMENT=production
```

`OPS_LOG_HUB_URL` は `https://<ops-log-hub-domain>/api/ingest/discord-bot` の形式です。

`OPS_LOG_HUB_URL` と `OPS_LOG_HUB_KEY` が未設定の場合、Bot はログ送信なしで動作します。

## 運用ログ

ops-log-hub を設定すると、以下のイベントを送信します。

- `startup`: Bot 起動完了
- `command_error`: slash command / prefix command の未処理エラー
- `config_error`: 起動時の拡張読み込みや slash command 同期の失敗

メッセージ本文、Token、Webhook URL などの secret は送信しません。

## 必要なDiscord権限

- チャンネルを見る
- メッセージを送信
- メッセージ履歴を読む
- スレッドを作成する
- プライベートスレッドを作成する
- スレッドを管理する
- ユーザーをスレッドへ招待する
- slash commandを使う

## 注意

現在の実装では `discord.Intents.all()` を使用しています。Discord Developer Portal 側の privileged intents 設定とコード側の intents 指定を一致させてください。
