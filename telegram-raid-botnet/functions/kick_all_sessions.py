import asyncio

from rich.progress import track
from rich.console import Console

from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest
from telethon import TelegramClient

from functions.base import TelethonFunction

console = Console()


class KickAllSessionsFunc(TelethonFunction):
    """Выгнать всех пользователей из сессий"""
    
    async def kick_all_sessions(self, session: TelegramClient):
        async with self.storage.ainitialize_session(session):
            try:
                authorizations = await session(GetAuthorizationsRequest())
            except Exception as error:
                console.print(f"Ошибка при получении авторизаций: {error}")
                return
            
            for authorization in authorizations.authorizations:
                if authorization.hash != 0:
                    try:
                        await session(ResetAuthorizationRequest(hash=authorization.hash))
                    except Exception as error:
                        console.print(f"Ошибка: {error}")
                    else:
                        console.print(f"Сброшена авторизация {authorization.ip} ({authorization.device_model}, {authorization.platform})")

    async def execute(self):
        await asyncio.gather(*[
            self.kick_all_sessions(session)
            for session in track(self.sessions, "Выгоняем...")
        ])