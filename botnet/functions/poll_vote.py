import asyncio
from rich.console import Console

from telethon import functions
from functions.base import TelethonFunction

console = Console()


class PollVoteFunc(TelethonFunction):
    """Голосование в опросе"""

    async def vote(self, session, channel, post_id, option_number):
        if not self.storage.initialize:
            await session.connect()

        await session(
            functions.messages.SendVoteRequest(
                peer=channel,
                msg_id=post_id,
                options=[str(option_number)]
            )
        )

    async def execute(self):
        self.ask_accounts_count()

        post_link = console.input("[bold red]Введите ссылку на сообщение/пост> ")
        option_number = int(console.input("[bold red]Введите число ответа (например 1, 2)> ")) - 1

        channel = post_link.split("/")[-2]
        post_id = int(post_link.split("/")[-1])

        with console.status("Голосование"):
            await asyncio.gather(*[
                self.vote(session, channel, post_id, option_number)
                for session in self.sessions
            ])