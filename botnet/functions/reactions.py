import asyncio
import random

from pyrogram import Client
from functions.base import PyrogramFunction
from rich.console import Console

console = Console()


class ReactionsFunc(PyrogramFunction):
    """Реакция на пост/соо"""

    reactions = ['👍', '❤️', '🔥', '🥰', '👏', '😁', '🎉', '🤩', '👎', '🤯', '😱', '🤬', '😢', '🤮', '💩', '🙏']

    async def set_reaction(self, session: Client, chat_username: str, message_id: int, reaction=None):
        if not reaction:
            reaction = random.choice(self.reactions)

        async with session:
            try:
                await session.send_reaction(
                    chat_id=chat_username,
                    message_id=int(message_id),
                    emoji=reaction 
                )
            except Exception as err:
                console.print(f"[bold red][ОШИБКА][/] [bold yellow][{session.me.id}][/] : {err}")
            else:
                console.print(f"[bold green][УСПЕХ] [{session.me.id}][/] : Реакция \"{reaction}\" была отправлена")


    async def execute(self):
        link_to_message = console.input("[bold red]Ссылка на сообщение/пост> [/]")
        chat_username, message_id = link_to_message.split("/")[-2:]

        reaction = console.input(
            "[bold red]Введите реакцию ({reactions}) или оставьте пустым для случайной> [/]"
            .format(reactions=", ".join(self.reactions))
        )

        await asyncio.gather(*[
            self.set_reaction(
                session=session,
                chat_username=chat_username,
                message_id=message_id,
                reaction=reaction
            )
            for session in self.sessions
        ]) 