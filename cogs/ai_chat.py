import discord
from discord.ext import commands
import asyncio
import os
import random
from .utils import (
    load_config, save_config,
    human_delay, simulate_typing,
    log_info, log_success, log_error,
)


class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = load_config()
        self.enabled: bool = cfg.get("ai_enabled", False)
        self.mode: str = cfg.get("ai_mode", "dm")        # dm | mentions | channel | all
        self.ai_channels: set = set(cfg.get("ai_channels", []))
        self.provider: str = cfg.get("ai_provider", "groq")
        # Per-channel conversation history (last 10 turns)
        self._history: dict = {}
        # Anti-loop: track last replied message id per channel
        self._last_reply: dict = {}

    # ── Internal helpers ────────────────────────────────────────────────────

    def _get_model(self) -> str:
        cfg = load_config()
        if self.provider == "openai":
            return cfg.get("ai_model_openai", "gpt-4o-mini")
        return cfg.get("ai_model_groq", "llama-3.3-70b-versatile")

    async def _call_llm(self, messages: list) -> str | None:
        cfg = load_config()
        persona = cfg.get(
            "ai_persona",
            "You are a chill person. Reply naturally in the same language as the user. Keep replies short.",
        )
        full = [{"role": "system", "content": persona}] + messages
        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            else:
                from groq import AsyncGroq
                client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

            resp = await client.chat.completions.create(
                model=self._get_model(),
                messages=full,
                max_tokens=400,
                temperature=0.85,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            log_error(f"AI error: {e}")
            return None

    def _should_reply(self, message: discord.Message) -> bool:
        """Decide whether to auto-reply based on current mode."""
        is_dm = isinstance(message.channel, discord.DMChannel)
        mentioned = self.bot.user in message.mentions

        if self.mode == "dm" and is_dm:
            return True
        if self.mode == "mentions" and mentioned:
            return True
        if self.mode == "channel" and message.channel.id in self.ai_channels:
            return True
        if self.mode == "dmmentions" and (is_dm or mentioned):
            return True
        if self.mode == "everyone":
            return True
        return False

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.command(name="ai")
    async def ai_cmd(self, ctx, action: str = "on", *, extra: str = ""):
        cfg = load_config()

        if action in ("on", "enable"):
            self.enabled = True
            cfg["ai_enabled"] = True
            save_config(cfg)
            msg = await ctx.send("🤖 AI auto-reply **enabled**")

        elif action in ("off", "disable"):
            self.enabled = False
            cfg["ai_enabled"] = False
            save_config(cfg)
            msg = await ctx.send("🤖 AI auto-reply **disabled**")

        elif action == "mode":
            valid = ("dm", "mentions", "channel", "dmmentions", "everyone")
            if extra.strip() in valid:
                self.mode = extra.strip()
                cfg["ai_mode"] = self.mode
                save_config(cfg)
                msg = await ctx.send(f"🤖 AI mode → **{self.mode}**")
            else:
                msg = await ctx.send(f"Valid modes: `dm` | `mentions` | `channel` | `dmmentions` | `everyone`")

        elif action == "persona":
            if extra.strip():
                cfg["ai_persona"] = extra.strip()
                save_config(cfg)
                msg = await ctx.send(f"🤖 AI persona updated.")
            else:
                current = cfg.get("ai_persona", "default")
                msg = await ctx.send(f"🤖 Current persona: {current}")

        elif action == "channel":
            if extra.strip().isdigit():
                cid = int(extra.strip())
                label_name = f"<#{cid}>"
            else:
                cid = ctx.channel.id
                label_name = ctx.channel.mention
            if cid in self.ai_channels:
                self.ai_channels.discard(cid)
                label = "removed from"
            else:
                self.ai_channels.add(cid)
                label = "added to"
            cfg["ai_channels"] = list(self.ai_channels)
            save_config(cfg)
            msg = await ctx.send(f"🤖 {label_name} {label} AI channels")

        elif action == "provider":
            if extra.strip() in ("groq", "openai"):
                self.provider = extra.strip()
                cfg["ai_provider"] = self.provider
                save_config(cfg)
                msg = await ctx.send(f"🤖 AI provider → **{self.provider}**")
            else:
                msg = await ctx.send("Valid providers: `groq` | `openai`")

        else:
            msg = await ctx.send(
                "Usage: `!s ai on/off` | `!s ai mode <dm/mentions/channel/all>` | `!s ai channel` | `!s ai provider <groq/openai>`"
            )

        await asyncio.sleep(6)
        try:
            await msg.delete()
        except Exception:
            pass

    @commands.command(name="analyze")
    async def analyze_cmd(self, ctx, member: discord.User = None):
        if not member:
            msg = await ctx.send("Usage: `!s analyze @user`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        status = await ctx.send(f"🔍 Analyzing **{member.name}**… give me a sec.")
        messages = []

        for guild in self.bot.guilds:
            if len(messages) >= 50:
                break
            for channel in guild.text_channels:
                if len(messages) >= 50:
                    break
                try:
                    async for m in channel.history(limit=300):
                        if m.author.id == member.id and m.content.strip():
                            messages.append(m.content)
                            if len(messages) >= 50:
                                break
                except Exception:
                    continue

        if not messages:
            await status.edit(content="❌ Not enough messages found for this user.")
            await asyncio.sleep(8)
            try:
                await status.delete()
            except Exception:
                pass
            return

        sample = "\n".join(f"• {m}" for m in messages[:30])
        prompt = [
            {
                "role": "user",
                "content": (
                    f'Analyze these Discord messages from user "{member.name}" and write a detailed, '
                    f"creative psychological portrait. Include:\n"
                    f"1. 🧠 Personality type (MBTI or Big Five)\n"
                    f"2. 💬 Communication style\n"
                    f"3. ❤️ Emotional patterns\n"
                    f"4. 🔍 Hidden traits\n"
                    f"5. 🎯 Likely interests\n"
                    f"6. ⚡ Overall vibe in one sentence\n\n"
                    f"Messages:\n{sample}\n\n"
                    f"Be insightful, creative, and a bit bold. Format nicely with emojis."
                ),
            }
        ]

        result = await self._call_llm(prompt)
        await status.delete()

        if result:
            full = f"🧠 **Psychological Portrait — {member.name}**\n\n{result}"
            chunks = [full[i:i+1990] for i in range(0, len(full), 1990)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            err = await ctx.send("❌ Failed to generate analysis. Check your API key in `.env`.")
            await asyncio.sleep(8)
            try:
                await err.delete()
            except Exception:
                pass

    # ── Listener ─────────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Only external users
        if message.author.id == self.bot.user.id:
            return
        if message.author.bot:
            return
        if not self.enabled:
            return

        # Let AFK cog handle mentions when active
        afk_cog = self.bot.get_cog("AFK")
        if afk_cog and afk_cog.afk_active:
            return

        if not self._should_reply(message):
            return

        # Anti-loop guard
        last = self._last_reply.get(message.channel.id)
        if last and last == message.id:
            return

        cid = message.channel.id
        if cid not in self._history:
            self._history[cid] = []

        self._history[cid].append({
            "role": "user",
            "content": f"{message.author.display_name}: {message.content}",
        })
        # Keep only last 10 turns
        self._history[cid] = self._history[cid][-10:]

        await simulate_typing(message.channel, random.uniform(1.2, 3.0))
        reply = await self._call_llm(self._history[cid])

        if reply:
            self._history[cid].append({"role": "assistant", "content": reply})
            chunks = [reply[i:i+1990] for i in range(0, len(reply), 1990)]
            sent = None
            for chunk in chunks:
                sent = await message.channel.send(chunk)
            self._last_reply[cid] = sent.id
            log_success(f"AI replied to {message.author.name} in {message.channel}")


async def setup(bot):
    await bot.add_cog(AIChat(bot))
