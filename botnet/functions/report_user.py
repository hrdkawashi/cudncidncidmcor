from rich.progress import track
from rich.console import Console
from rich.prompt import Prompt

from telethon import types, functions
from functions.base import TelethonFunction

console = Console()

class ReportFunc(TelethonFunction):
    """Жалоба на юзернейм"""

    def __init__(self, storage, settings):
        super().__init__(storage, settings)

        self.reasons = (
            ("Жестокое обращение с детьми", types.InputReportReasonChildAbuse()),
            ("Авторские права", types.InputReportReasonCopyright()),
            ("Фальшивый канал/аккаунт", types.InputReportReasonFake()),
            ("Порнография", types.InputReportReasonPornography()),
            ("Спам", types.InputReportReasonSpam()),
            ("Насилие", types.InputReportReasonViolence()),
            ("Прочее", types.InputReportReasonOther())
        )

    async def execute(self):
        self.ask_accounts_count()

        link = Prompt.ask("[bold red]имя пользователя>[/]")

        print()

        for index, reasons in enumerate(self.reasons):
            reason, _ = reasons

            console.print(
                "[bold white][{}] {}[/]"
                .format(index + 1, reason)
            )

        print()

        choice = int(console.input("[bold white]>> [/]"))
        reason_type = self.reasons[choice - 1][1]

        comment = console.input("[bold red]комментарий> [/]")

        for index, session in track(
            enumerate(self.sessions),
            "[yellow]Отправка отчёта...[/]",
            total=len(self.sessions)
        ):
            async with self.storage.ainitialize_session(session):
                me = await session.get_me()
                try:
                    await session(
                        functions.account.ReportPeerRequest(
                            peer=link,
                            reason=reason_type,
                            message=comment
                        )
                    )
                except Exception as err:
                    console.print(
                        "[{name}] [bold red]ошибка.[/] {error}"
                        .format(name=me.first_name, error=err)
                    )
