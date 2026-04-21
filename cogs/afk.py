import discord
from discord.ext import commands
import asyncio
from .utils import log_info, log_success


class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_active: bool = False
        self.afk_message: str = "I'm AFK right now, I'll be back soon!"
        self._notified: set = set()
        self._setting_afk: bool = False

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.command(name="afk")
    async def afk_cmd(self, ctx, *, message: str = None):
        self._setting_afk = True
        if message is None or message.lower() == "off":
            self.afk_active = False
            self._notified.clear()
            msg = await ctx.send("✅ AFK mode **disabled**. Welcome back!")
        else:
            self.afk_active = True
            self.afk_message = message
            self._notified.clear()
            msg = await ctx.send(f"💤 AFK mode **enabled** — *{message}*")
            log_info(f"AFK active: {message}")

        await asyncio.sleep(6)
        try:
            await msg.delete()
        except Exception:
            pass
        self._setting_afk = False

    # ── Listener ─────────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            prefix = self.bot.command_prefix
            if self.afk_active and not self._setting_afk and not message.content.startswith(prefix):
                self.afk_active = False
                self._notified.clear()
                log_success("AFK auto-disabled (you sent a message)")
            return

        if not self.afk_active:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        mentioned = self.bot.user in message.mentions

        if not is_dm and not mentioned:
            return

        if message.author.id in self._notified:
            return

        self._notified.add(message.author.id)
        reply = f"💤 **{self.bot.user.display_name}** is currently AFK — {self.afk_message}"

        try:
            await message.channel.send(reply)
            log_info(f"AFK: notified {message.author.name}")
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AFK(bot))
