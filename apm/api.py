from discord import Client, Intents
from discord.app_commands import CommandTree

from twitchio.ext.commands import Bot


class DiscordBot(Client):
    def __init__(self, token: str, intents: Intents | None):
        self.token = token

        if intents is None:
            intents = Intents.default()

        super().__init__(intents=intents)

        self.tree = CommandTree(self)

        @self.event
        async def on_ready(self):
            await self.tree.sync()

    def run(self):
        super().run(self.token)


class TwitchBot(Bot):
    def __init__(self, token: str, prefix: str, initial_channels: list[str]) -> None:
        super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)


__all__ = ["DiscordBot", "TwitchBot"]
