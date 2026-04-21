import discord
from discord.ext import commands
import asyncio
import datetime
import os
import aiohttp
from .utils import load_config, save_config, log_info, log_warn


class KeywordLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = load_config()
        self.keywords: list = cfg.get("keywords", [])
        self.log_file: str = cfg.get("keyword_log_file", "logs/keywords.txt")
        self.webhook_url: str = cfg.get("keyword_webhook", "")
        # In-memory message cache for deleted message recovery
        self._cache: dict = {}
        os.makedirs("logs", exist_ok=True)

    # ── Internal helpers ────────────────────────────────────────────────────

    def _ts(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def _log(self, message: discord.Message, matched: str, deleted: bool = False):
        ts = self._ts()
        guild = message.guild.name if message.guild else "DM"
        channel = getattr(message.channel, "name", "DM")
        flag = "[DELETED] " if deleted else ""
        entry = (
            f"[{ts}] {flag}[{guild} #{channel}] "
            f"{message.author} → {message.content!r}  (match: {matched})\n"
        )

        # Write to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)

        label = "🗑️ DELETED keyword" if deleted else "🔍 Keyword"
        log_info(f"{label} '{matched}' from {message.author.name}")

        # Send to webhook if configured
        if self.webhook_url:
            asyncio.create_task(self._send_webhook(message, matched, ts, deleted))

    async def _send_webhook(
        self,
        message: discord.Message,
        matched: str,
        ts: str,
        deleted: bool,
    ):
        guild = str(message.guild) if message.guild else "DM"
        channel = str(message.channel)
        color = 0xFF4444 if deleted else 0x5865F2
        title = f"{'🗑️ Deleted message — ' if deleted else ''}Keyword: `{matched}`"

        payload = {
            "username": "Keyword Logger",
            "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png",
            "embeds": [
                {
                    "title": title,
                    "description": message.content or "*[no content]*",
                    "color": color,
                    "fields": [
                        {"name": "Author", "value": str(message.author), "inline": True},
                        {"name": "Channel", "value": f"#{channel}", "inline": True},
                        {"name": "Server", "value": guild, "inline": True},
                    ],
                    "footer": {"text": ts},
                }
            ],
        }
        try:
            async with aiohttp.ClientSession() as s:
                await s.post(self.webhook_url, json=payload)
        except Exception as e:
            pass  # Silently fail webhook

    def _is_match(self, message: discord.Message) -> str | None:
        """Return the first matched keyword, or None."""
        if self.bot.user in message.mentions:
            return f"@{self.bot.user.name}"
        lo = message.content.lower()
        for kw in self.keywords:
            if kw.lower() in lo:
                return kw
        return None

    # ── Listeners ────────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        # Cache every message for deleted-message recovery
        self._cache[message.id] = message
        if len(self._cache) > 2000:
            oldest = next(iter(self._cache))
            del self._cache[oldest]

        matched = self._is_match(message)
        if matched:
            await self._log(message, matched)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        msg = self._cache.get(payload.message_id)
        if not msg:
            return
        matched = self._is_match(msg)
        if matched:
            await self._log(msg, matched, deleted=True)

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.command(name="kw")
    async def kw_cmd(self, ctx, action: str = "list", *, word: str = None):
        cfg = load_config()

        if action == "add" and word:
            if word not in self.keywords:
                self.keywords.append(word)
                cfg["keywords"] = self.keywords
                save_config(cfg)
            msg = await ctx.send(f"✅ Keyword added: `{word}`")

        elif action == "remove" and word:
            if word in self.keywords:
                self.keywords.remove(word)
                cfg["keywords"] = self.keywords
                save_config(cfg)
            msg = await ctx.send(f"✅ Keyword removed: `{word}`")

        elif action == "clear":
            self.keywords.clear()
            cfg["keywords"] = []
            save_config(cfg)
            msg = await ctx.send("✅ All keywords cleared.")

        elif action == "list":
            if self.keywords:
                kws = " • ".join(f"`{k}`" for k in self.keywords)
            else:
                kws = "*No keywords set*"
            msg = await ctx.send(f"🔍 **Keywords:** {kws}")

        elif action == "webhook":
            self.webhook_url = word or ""
            cfg["keyword_webhook"] = self.webhook_url
            save_config(cfg)
            state = "set" if self.webhook_url else "cleared"
            msg = await ctx.send(f"🔗 Keyword webhook {state}.")

        else:
            msg = await ctx.send(
                "Usage: `!s kw add <word>` | `!s kw remove <word>` | `!s kw list` | `!s kw clear` | `!s kw webhook <url>`"
            )

        await asyncio.sleep(8)
        try:
            await msg.delete()
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(KeywordLogger(bot))
