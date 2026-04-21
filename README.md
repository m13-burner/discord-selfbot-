# 🤖 Selfbot

A Discord selfbot built with `discord.py-self` featuring AI auto-reply, AFK, keyword logger, and utility commands.

---

## ✨ Features

- 🤖 **AI Auto-reply** — Automatically replies to DMs or mentions using Groq (free) or OpenAI
- 🧠 **Analyze** — Generates a psychological portrait of any user based on their messages
- 💤 **AFK** — Auto-replies when you're mentioned while AFK
- 🔍 **Keyword Logger** — Logs messages containing specific keywords (supports webhooks)
- 🗑️ **Purge** — Deletes your last N messages in a channel
- 📩 **DM** — DM anyone by mention, username, or ID
- ⏳ **Schedule** — Send a message after a delay (`10s`, `5m`, `1h`)
- 🏓 **Ping** — Check bot latency

---

## 🚀 Setup

**1. Install dependencies**
```
pip install -r requirements.txt
```

**2. Fill in your `.env`**
```env
DISCORD_TOKEN=your_token_here
GROQ_API_KEY=your_groq_key_here  # free at console.groq.com
```

**3. Run**
```
python main.py
```

---

## ⚙️ Configuration

Edit `config.json` to change:
- `prefix` — command prefix (default: `!s `)
- `ai_mode` — `dm`, `mentions`, `channel`, or `all`
- `ai_persona` — customize the AI's personality
- `ai_model_groq` — Groq model to use (default: `llama-3.3-70b-versatile`)

---

## 📋 Commands

| Command | Description |
|---|---|
| `!s ai on/off` | Toggle AI auto-reply |
| `!s ai mode <dm/mentions>` | Set AI response mode |
| `!s analyze @user` | Psychological portrait |
| `!s afk <message>` | Set AFK message |
| `!s afk off` | Disable AFK |
| `!s kw add <word>` | Add keyword to log |
| `!s kw remove <word>` | Remove keyword |
| `!s kw list` | List keywords |
| `!s purge [n]` | Delete your last N messages |
| `!s dm @user <msg>` | DM someone directly |
| `!s schedule 10s <msg>` | Schedule a message |
| `!s ping` | Check latency |

---

## 🔒 Full Version — $8

The full version includes everything in base plus:

- 👤 **Profile Copy** — Copy any user's avatar, banner, bio, display name, clan tag, status
- 🎯 **Vanity Checker** — Get notified when a vanity URL becomes available
- 📨 **Mass DM** — DM all members in a server
- 🎁 **Nitro Sniper** — Auto-claim Nitro gift links
- 🎮 **Rich Presence** — Custom Discord rich presence
- 🌀 **Dynamic Status** — Rotating custom statuses
- ⚡ **Auto React** — Auto-react to messages from specific users
- 📊 **Server Info** — Detailed server/member/role info
- 💾 **Account Backup** — Backup your account data
- 🔐 **NopeCHA Captcha Solver** — Automatically solves Discord captchas

👉 **Join discord.gg/g0d to purchase**

---

## ⚠️ Disclaimer

This project is for educational purposes only. Using selfbots violates Discord's Terms of Service. Use at your own risk.

---

**Dev:** @_m13 • **Server:** discord.gg/g0d
