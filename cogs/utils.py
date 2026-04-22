import asyncio
import random
import json
import datetime
from colorama import Fore, Style
from discord.ext import commands


# ─── Config helpers ───────────────────────────────────────────────────────────

def load_config() -> dict:
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data: dict):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ─── Human simulation ─────────────────────────────────────────────────────────

async def human_delay(min_s: float = 1.0, max_s: float = 3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def simulate_typing(channel, duration: float = 2.0):
    async with channel.typing():
        await asyncio.sleep(duration)


# ─── Console logging ──────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def log_info(msg: str):
    print(f"{Fore.CYAN}[{_ts()}] [INFO]  {msg}{Style.RESET_ALL}")


def log_success(msg: str):
    print(f"{Fore.GREEN}[{_ts()}] [OK]    {msg}{Style.RESET_ALL}")


def log_warn(msg: str):
    print(f"{Fore.YELLOW}[{_ts()}] [WARN]  {msg}{Style.RESET_ALL}")


def log_error(msg: str):
    print(f"{Fore.RED}[{_ts()}] [ERROR] {msg}{Style.RESET_ALL}")


# ─── Cog ──────────────────────────────────────────────────────────────────────

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        text = (
            "```md\n"
            "# 🤖 Selfbot Commands\n\n"
            "## AI\n"
            "!s ai on/off                   — Toggle AI auto-reply\n"
            "!s ai mode dm                  — DMs only\n"
            "!s ai mode mentions            — Mentions only\n"
            "!s ai mode dmmentions          — DMs + mentions\n"
            "!s ai mode channel             — Reply in set channels only\n"
            "!s ai mode everyone            — Reply to every message\n"
            "!s ai channel                  — Toggle current channel\n"
            "!s ai persona <text>           — Set AI personality\n"
            "!s analyze @user               — Psychological portrait\n\n"
            "## AFK\n"
            "!s afk <message>               — Set AFK message\n"
            "!s afk off                     — Disable AFK\n\n"
            "## Keyword Logger\n"
            "!s kw add <word>         — Add keyword to log\n"
            "!s kw remove <word>      — Remove keyword\n"
            "!s kw list               — List keywords\n\n"
            "## Tools\n"
            "!s purge [n]             — Delete your last N messages\n"
            "!s dm @user <msg>        — DM someone directly\n"
            "!s schedule 10s <msg>    — Send a message after a delay\n\n"
            "## System\n"
            "!s ping                  — Check bot latency\n"
            "```\n"
            "🔒 **Full version** ($8 one-time) includes: Profile Copy, Vanity Checker, Mass DM, Nitro Sniper, Rich Presence, Dynamic Status, Auto React, Server Info, Backup & more.\n"
            "👉 **discord.gg/g0d**"
        )
        msg = await ctx.send(text)
        await asyncio.sleep(25)
        try:
            await msg.delete()
        except Exception:
            pass

    @commands.command(name="ping")
    async def ping_cmd(self, ctx):
        ms = round(self.bot.latency * 1000)
        msg = await ctx.send(f"🏓 Pong! **{ms}ms**")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Utils(bot))
