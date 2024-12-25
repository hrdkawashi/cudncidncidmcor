import asyncio
from telethon.tl.functions.account import UpdateProfileRequest
from rich.console import Console
from functions.base import TelethonFunction

console = Console()


class ChangeBioFunc(TelethonFunction):
    """Изменить био"""
    
    async def change_bio(self, session, bio: str):
        async with self.storage.ainitialize_session(session):
            await session(
                UpdateProfileRequest(about=bio)
            )

    async def execute(self):
        bio = console.input("[bold red]био> [/]")
        
        await asyncio.gather(*[
            self.change_bio(session, bio)
            for session in self.sessions
        ])