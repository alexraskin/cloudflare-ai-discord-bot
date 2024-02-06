import logging
import os

import discord
from cogs import EXTENSIONS
from discord.ext.commands import Bot, NoEntryPointError
from dotenv import load_dotenv

load_dotenv() 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Discord")


class CloudflareAIBot(Bot):
    def __init__(self, *args, **options) -> None:
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True
        )
        intents = discord.Intents(
            emojis=True,
            messages=True,
            reactions=True,
            message_content=True,
            guilds=True,
            guild_messages=True,
        )
        super().__init__(
            *args,
            allowed_mentions=allowed_mentions,
            intents=intents,
            heartbeat_timeout=150.0,
            **options,
        )
        self.log = log

    async def start(self, *args, **kwargs) -> None:
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await super().close()

    async def on_ready(self) -> None:
        #await self.tree.sync()
        self.log.info(f"Ready: {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        for cog in EXTENSIONS:
            try:
                await self.load_extension(cog)
                self.log.info(f"Loaded extension: {cog}")
            except NoEntryPointError:
                self.log.error(
                    f"Could not load extension: {cog} due to NoEntryPointError"
                )
            except Exception as exc:
                self.log.error(
                    f"Could not load extension: {cog} due to {exc.__class__.__name__}: {exc}"
                )


if __name__ == "__main__":
    client: CloudflareAIBot = CloudflareAIBot(
        command_prefix=os.getenv("PREFIX", ">"),
        description=str("Discord bot, which can interact with the Cloudflare AI."),
    )
    client.run(
        token=os.getenv("DISCORD_TOKEN"),
    )
