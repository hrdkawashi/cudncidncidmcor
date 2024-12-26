import asyncio

from rich.console import Console
from rich.markup import escape

from telethon import TelegramClient
from functions.base import TelethonFunction

console = Console()

class SetPasswordFunc(TelethonFunction):
    """Установить 2ФА(пар)"""
    
    async def edit_2fa(self, session: TelegramClient, password: str):
        async with self.storage.ainitialize_session(session):
            me = await session.get_me()

            try:
                await session.edit_2fa(new_password=password)
            except Exception as err:
                console.print(
                    "[{name}] : [bold red]Пароль не изменён[/]. Ошибка: {error}"
                    .format(name=escape(me.first_name), error=err)
                )
            else:
                console.print(
                    "[{name}] : [bold green]Пароль успешно обновлён"
                    .format(name=escape(me.first_name))
                )

    async def execute(self):
        password = console.input("[bold red]новый пароль> [/]")
        
        with console.status("Установка пароля..."):
            await asyncio.wait([
                self.edit_2fa(session=session, password=password)
                for session in self.sessions
            ])