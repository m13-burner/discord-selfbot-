import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv
from colorama import Fore, Style, init
import datetime

init(autoreset=True)
load_dotenv()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

PREFIX = config.get("prefix", "!s ")


class SelfBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            self_bot=True,
            help_command=None,
        )
        self.config = config
        self.start_time = datetime.datetime.utcnow()

    async def setup_hook(self):
        cogs = [
            "cogs.utils",
            "cogs.ai_chat",
            "cogs.afk",
            "cogs.keyword_logger",
            "cogs.tools",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"{Fore.GREEN}  [✓] {cog}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  [✗] {cog}: {e}{Style.RESET_ALL}")

    async def on_ready(self):
        ping = round(self.latency * 1000)
        tag = f"{self.user.name}#{self.user.discriminator}" if self.user.discriminator != "0" else self.user.name
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║       🤖   SELFBOT  ACTIVATED   🤖       ║
╠══════════════════════════════════════════╣
║  User    : {tag:<30}║
║  ID      : {str(self.user.id):<30}║
║  Servers : {str(len(self.guilds)):<30}║
║  Prefix  : {PREFIX:<30}║
║  Ping    : {str(ping) + 'ms':<30}║
╠══════════════════════════════════════════╣
║  Dev     : @_m13                         ║
║  Server  : discord.gg/g0d                ║
╠══════════════════════════════════════════╣
║  🔒 Full version ($8) — discord.gg/g0d   ║
╠══════════════════════════════════════════╣
║  FULL INCLUDES:                          ║
║  • Profile Copy + Clan Tag + Save/Restore║
║  • Vanity Checker                        ║
║  • Mass DM                               ║
║  • Nitro Sniper                          ║
║  • Rich Presence                         ║
║  • Dynamic Status Rotation               ║
║  • Auto React                            ║
║  • Server Info / Members / Roles         ║
║  • Account Backup                        ║
║  • NopeCHA Captcha Solver                ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}""")

    async def on_command(self, ctx):
        if self.config.get("auto_delete_commands", True):
            delay = self.config.get("auto_delete_delay", 2)
            asyncio.create_task(self._delete_after(ctx.message, delay))

    async def on_message(self, message):
        if message.author.id != self.user.id:
            return
        await self.process_commands(message)

    async def _delete_after(self, message, delay: float):
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        print(f"{Fore.RED}[ERROR] {error}{Style.RESET_ALL}")


bot = SelfBot()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print(f"{Fore.RED}[!] DISCORD_TOKEN not found in .env — fill in your token!{Style.RESET_ALL}")
        exit(1)
    bot.run(token)
