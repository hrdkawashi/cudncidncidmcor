import asyncio
import random

from typing import List, Tuple, Optional
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
from rich.console import Console
from functions.base import TelethonFunction

console = Console()


class ChangeNameFunc(TelethonFunction):
    """Изменение имени"""
    
    @staticmethod
    def get_random_name(names: List[str]) -> Tuple[str, Optional[str]]:
        name = random.choice(names).split()
        
        if len(name) == 1:
            return name, None

        return name
    
    async def change_name(
        self,
        session: TelegramClient,
        account_index: int,
        names: Optional[List[str]] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ):
        if names is not None:
            first_name, last_name = self.get_random_name(names)

        async with self.storage.ainitialize_session(session):
            me = await session.get_me()
            
            full_name = me.first_name + (" " + me.last_name if me.last_name else "")

            try:
                await session(
                    UpdateProfileRequest(
                        first_name=first_name,
                        last_name=last_name or ""
                    )
                )
            except Exception as error:
                console.print(f"[bold red][!][/] {error}")
            else:
                console.print(f"Имя успешно изменено [bold green]успешно.[/] ( {full_name} → {first_name} {last_name or ''} )")

    async def execute(self):
        self.ask_accounts_count()

        from_file = console.input("[bold red]Из файла? (y/n)> ")

        if from_file == "y":
            with open("assets/names.txt") as file:
                names = file.read().strip().splitlines()

            await asyncio.gather(*[
                self.change_name(session=session, account_index=index, names=names)
                for index, session in enumerate(self.sessions)
            ])

        else:
            name = console.input("[bold red]Имя> [/]").split(maxsplit=1)
            print()
            
            first_name = name[0]
            
            if len(name) == 2:
                last_name = name[1]
            else:
                last_name = None

            await asyncio.gather(*[
                self.change_name(
                    session=session,
                    account_index=index,
                    first_name=first_name,
                    last_name=last_name
                )
                for index, session in enumerate(self.sessions)
            ])