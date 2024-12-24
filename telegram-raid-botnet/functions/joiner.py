
import random
import asyncio

from rich.progress import track
from rich.console import Console
from rich.prompt import Prompt, Confirm

from time import perf_counter

from telethon import events, types
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.sync import TelegramClient

from functions.flood import Flood
from functions.base import TelethonFunction

console = Console()


class JoinerFunc(TelethonFunction):
    """Присоединение к чату"""

    async def join(self, session, link, index, mode):
        if mode == "1":
            try:
                if not "joinchat" in link:
                    await session(JoinChannelRequest(link))
                else:
                    invite = link.split("/")[-1]
                    await session(ImportChatInviteRequest(invite))
            except Exception as error:
                print(f"[-] [акк {index + 1}] {error}")
            else:
                return True

        elif mode == "2":
            try:
                channel = await session(GetFullChannelRequest(link))
                chat = channel.chats[1]
                await session(JoinChannelRequest(chat))
            except Exception as error:
                print(f"[-] [акк {index + 1}] {error}")
            else:
                return True

    async def solve_captcha(self, session: TelegramClient):
        session.add_event_handler(
            self.on_message,
            events.NewMessage
        )

        await session.run_until_disconnected()

    async def on_message(self, msg: types.Message):
        if msg.mentioned:
            if msg.reply_markup:
                captcha = msg.reply_markup.rows[0] \
                    .buttons[0].data.decode("utf-8")

                await msg.click(data=captcha)

    async def execute(self):
        self.ask_accounts_count()

        print()

        console.print(
            "[1] Просто присоединиться к чату/каналу",
            "[2] Присоединиться к чату, связанному с каналом",
            sep="\n",
            style="bold white"
        )

        print()

        mode = console.input("[bold red]режим> [/]")
        link = console.input("[bold red]ссылка> [/]")
        
        link = link.replace("+", "joinchat/")

        speed = Prompt.ask(
            "[bold red]скорость>[/]",
            choices=["нормальная", "быстрая"]
        )

        flood = Confirm.ask("[bold red]флудить сразу?[/]")

        if flood:
            flood_func = Flood(self.storage, self.settings)
            function_index = flood_func.ask()

        else:
            function_index = None

        joined = 0

        if speed == "нормальная":
            delay = Prompt.ask("[bold red]задержка[/]", default="0")
            captcha = Confirm.ask("[bold red]капча[/]")

            start = perf_counter()

            if function_index != 1:
                for index, session in track(
                    enumerate(self.sessions),
                    "[yellow]Присоединение[/]",
                    total=len(self.sessions)
                ):
                    await session.start()

                    if captcha:
                        asyncio.create_task(
                            self.solve_captcha(session)
                        )

                    is_joined = await self.join(session, link, index, mode)

                    if is_joined:
                        joined += 1

                    await asyncio.sleep(int(delay))
            
            elif function_index == 1:
                for index, session in enumerate(self.sessions):
                    await session.start()

                    if captcha:
                        asyncio.create_task(
                            self.solve_captcha(session)
                        )

                    is_joined = await self.join(session, link, index, mode)

                    console.print("[bold green]Бот присоединился[/]")

                    if is_joined:
                        joined += 1
                    
                    console.print("[bold white]Запуск спама[/]")
                    
                    await flood_func.flood(session, link, flood_func.function)
                    await asyncio.sleep(int(delay))

        if speed == "быстрая":
            if not self.storage.initialize:
                for session in track(
                    self.sessions,
                    "[yellow]Инициализация сессий[/]",
                    total=len(self.sessions)
                ):
                    await session.connect()

            with console.status("Присоединение"):
                start = perf_counter()

                results = await asyncio.gather(*[
                    self.join(session, link, index, mode)
                    for index, session in enumerate(self.sessions)
                ])

            for result in results:
                if result:
                    joined += 1


        joined_time = round(perf_counter() - start, 2)
        console.print(f"[+] {joined} ботов присоединилось за [yellow]{joined_time}[/]с")

        if flood and function_index != 1:
            await asyncio.gather(*[
                flood_func.flood(session, link, flood_func.function)
                for session in self.sessions
            ])