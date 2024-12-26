import asyncio

from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError

from rich.prompt import Prompt
from rich.console import Console

from functions.base import TelethonFunction
console = Console()


class InvitingFunc(TelethonFunction):
    """Приглашение из чата"""

    @staticmethod
    def transform_to_valid_invite(link):
        """Преобразует ссылку в правильный формат приглашения"""
        if "t.me" in link:
            if "joinchat" in link:
                invite = link.split("/")[-1]
            else:
                invite = "@" + link.split("/")[-1]
        elif link.startswith("@"):
            invite = link

        return invite

    @staticmethod
    def chunkify(lst, n):  # Разбивает список на части
        return [lst[i::n] for i in range(n)]
   
    async def invite(self, users, channel, session):
        """Приглашает пользователей в канал"""
        users_for_invite = []

        async with self.storage.ainitialize_session(session):
            channel = await session.get_entity(channel)
            for user in users: 
                if user.username:
                    user = await session.get_entity(user.username)
                    users_for_invite.append(user)

            for user in users_for_invite:
                try:
                    await session(InviteToChannelRequest(
                        channel=channel,
                        users=[user]
                    ))
                except PeerFloodError as err:
                    console.print(f"[bold red]{err}[/]")
                    return
                except UserPrivacyRestrictedError:
                    pass

    async def execute(self):
        """Основной метод для выполнения приглашения"""
        accounts_count = int(Prompt.ask(
            "[bold magenta]Сколько аккаунтов использовать?[/]",
            default=str(len(self.sessions))
        ))

        self.sessions = self.sessions[:accounts_count]

        link = console.input("[bold red]Ссылка на чат> [/]")
        invite = self.transform_to_valid_invite(link)

        session = None

        with console.status("Парсинг пользователей...", spinner="dots"):
            for session in self.sessions:
                await session.connect()

                try:
                    if "@" in invite:
                        await session(JoinChannelRequest(invite))
                    else:
                        await session(ImportChatInviteRequest(invite))
                except Exception as err:
                    console.print(err)
                    await session.disconnect()
                    continue
                else:
                    break

            users = await session.get_participants(link, aggressive=False)

        console.print(
            "[bold green][*] Найдено {} пользователей[/]"
            .format(len(users))
        )

        users = self.chunkify(users, len(self.sessions))

        link = console.input("[bold red]Куда пригласить пользователей> [/]")

        with console.status("Приглашение пользователей...", spinner="dots"):
            await asyncio.gather(*[
                self.invite(users_chunk, link, session)
                for session, users_chunk in zip(self.sessions, users)
            ])
