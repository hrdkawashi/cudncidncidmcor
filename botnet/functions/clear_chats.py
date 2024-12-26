import asyncio

from telethon import functions, types, TelegramClient
from rich.console import Console
from rich.prompt import Confirm

from functions.base import TelethonFunction

console = Console()


class ClearDialogsFunc(TelethonFunction):
    """Очистить чаты"""

    async def clear(self, session: TelegramClient):
        async with self.storage.ainitialize_session(session):
            async for dialog in session.iter_dialogs():
                if not isinstance(dialog.entity, types.Channel):
                    await session(functions.messages.DeleteHistoryRequest(
                        peer=dialog.entity,
                        max_id=0,
                        just_clear=True,
                        revoke=True
                    ))
                else:
                    await session(
                        functions.channels.LeaveChannelRequest(dialog.id)
                    )

                console.log(f"Чат {dialog.id} | {dialog.title} был удален.")

    async def execute(self):
        confirm = Confirm.ask("[bold red]Вы уверены?[/]")

        if confirm:
            await asyncio.gather(*[
                self.clear(session)
                for session in self.sessions
            ])

