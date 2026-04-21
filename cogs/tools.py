import discord
from discord.ext import commands
import asyncio
from .utils import log_info, log_success, log_error


def _parse_duration(s: str) -> float | None:
    s = s.strip().lower()
    try:
        if s.endswith("s"):
            return float(s[:-1])
        if s.endswith("m"):
            return float(s[:-1]) * 60
        if s.endswith("h"):
            return float(s[:-1]) * 3600
        return float(s)
    except ValueError:
        return None


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Purge ─────────────────────────────────────────────────────────────────

    @commands.command(name="purge")
    async def purge_cmd(self, ctx, amount: int = 10):
        deleted = 0
        async for message in ctx.channel.history(limit=200):
            if deleted >= amount:
                break
            if message.author.id == self.bot.user.id:
                try:
                    await message.delete()
                    deleted += 1
                    await asyncio.sleep(0.4)
                except Exception:
                    pass

        msg = await ctx.send(f"🗑️ Deleted **{deleted}** of your messages.")
        log_success(f"Purged {deleted} messages in #{ctx.channel.name}")
        await asyncio.sleep(4)
        try:
            await msg.delete()
        except Exception:
            pass

    # ── DM ────────────────────────────────────────────────────────────────────

    @commands.command(name="dm")
    async def dm_cmd(self, ctx, target: str = None, *, message: str = None):
        if not target or not message:
            msg = await ctx.send("❌ Usage: `!s dm @user <message>` or `!s dm userID <message>`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        member = None
        target = target.strip().lstrip("@")
        if ctx.guild:
            if target.isdigit():
                member = ctx.guild.get_member(int(target))
            if member is None:
                uid = target[2:-1].lstrip("!") if target.startswith("<@") and target.endswith(">") else None
                if uid and uid.isdigit():
                    member = ctx.guild.get_member(int(uid))
            if member is None:
                member = discord.utils.find(
                    lambda m: m.name.lower() == target.lower() or m.display_name.lower() == target.lower(),
                    ctx.guild.members,
                )

        if member is None and target.isdigit():
            try:
                member = await self.bot.fetch_user(int(target))
            except Exception:
                pass

        if member is None:
            msg = await ctx.send(f"❌ Could not find user `{target}`.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        try:
            await member.send(message)
            log_success(f"DM sent to {member.name}")
            msg = await ctx.send(f"✅ DM sent to **{member.display_name}**.")
        except discord.Forbidden:
            msg = await ctx.send(f"❌ Can't DM **{member.display_name}** — their DMs are closed.")
        except Exception as e:
            log_error(f"DM failed: {e}")
            msg = await ctx.send(f"❌ Failed to DM: {e}")

        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass

    # ── Schedule ──────────────────────────────────────────────────────────────

    @commands.command(name="schedule", aliases=["sched"])
    async def schedule_cmd(self, ctx, delay: str = None, *, message: str = None):
        if not delay or not message:
            msg = await ctx.send("❌ Usage: `!s schedule 10s <message>` — supports s/m/h")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        seconds = _parse_duration(delay)
        if seconds is None or seconds <= 0:
            msg = await ctx.send("❌ Invalid duration. Use `10s`, `5m`, `1h`, etc.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        confirm = await ctx.send(f"⏳ Message scheduled in **{delay}**.")
        await asyncio.sleep(3)
        try:
            await confirm.delete()
        except Exception:
            pass

        log_info(f"Scheduled message in {delay}: {message[:50]}")
        await asyncio.sleep(seconds)
        await ctx.send(message)



async def setup(bot):
    await bot.add_cog(Tools(bot))
