import asyncio
import random
import os
from telethon import functions, types
from rich.prompt import Prompt, Confirm
from rich.console import Console

from functions.base import TelethonFunction

console = Console()


class PmFloodFunc(TelethonFunction):
    """Спам в ЛС"""

    async def flood(self, session, peer, text, media, by_phone_number):
        count = 0
        errors = 0

        async with self.storage.ainitialize_session(session):
            try:
                me = await session.get_me()
            except:
                return
            
            if by_phone_number:
                result = await session(functions.contacts.ImportContactsRequest(
                    contacts=[types.InputPhoneContact(
                        client_id=random.randrange(-2**63, 2**63),
                        phone=peer,
                        first_name='owned by eucult',
                        last_name=''
                    )]
                ))
                
                peer = result.users[0]

            while True:
                try:
                    if not media:
                        await session.send_message(peer, text)
                    else:
                        file = random.choice(os.listdir("media"))

                        await session.send_file(
                            peer,
                            os.path.join("media", file),
                            caption=text,
                            parse_mode="html"
                        )
                except Exception as err:
                    console.print(
                        "[{name}] [bold red]не отправлено.[/] {err}"
                        .format(name=me.first_name, err=err)
                    )

                    if errors >= 5:
                        break

                    errors += 1
                else:
                    count += 1
                    console.print(
                        "[{name}] [bold green]отправлено.[/] СЧЁТ: [yellow]{count}[/]"
                        .format(name=me.first_name, count=count)
                    )
                finally:
                    await self.delay()

    async def execute(self):
        self.ask_accounts_count()

        console.print()
        console.print("[bold white][1] Спам по имени пользователя")
        console.print("[bold white][2] Спам по номеру телефона")
        choice = console.input("\n[bold white]>> ")
        
        by_phone_number = False
        
        if choice == "1":
            peer = console.input("[bold red]введите имя пользователя> [/]")
        elif choice == "2":
            by_phone_number = True
            peer = console.input("[bold red]введите номер телефона> [/]")
        else:
            console.print("[bold red]Неверный ввод!")
            return

        media = Confirm.ask("[bold red]медиа")
        text = console.input("[bold red]текст> [/]")

        delay = Prompt.ask(
            "[bold red]задержка[/]",
            default="-".join(str(x) for x in self.settings.delay)
        )

        self.settings.delay = self.parse_delay(delay)

        await asyncio.gather(*[
            self.flood(session, peer, text, media, by_phone_number=by_phone_number)
            for session in self.sessions
        ])