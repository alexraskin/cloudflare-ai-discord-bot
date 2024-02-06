from __future__ import annotations

from typing import Optional

from discord import HTTPException
from discord.ext import commands


class Admin(commands.Cog, name="Admin"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        """
        Sync app commands with Discord.
        """
        await ctx.message.delete()
        message = await ctx.send(content="Syncing... 🔄")
        try:
            await self.client.tree.sync()
        except HTTPException as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send("An error occurred while syncing.", ephemeral=True)
            return
        sync_message = await message.edit(content="Synced successfully! ✅")
        await sync_message.delete(delay=5)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Admin(client))
