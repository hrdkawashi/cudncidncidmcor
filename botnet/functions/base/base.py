import asyncio
import random
from rich.prompt import Prompt


class BaseFunction:
    def parse_delay(self, string: str):
        return list(
            map(int, string.split("-"))
        )

    def ask_accounts_count(self):
        accounts_count = int(Prompt.ask(
            "[bold magenta]Сколько использовать аккаунтов? [/]",
            default=str(len(self.sessions))
        ))

        self.sessions = self.sessions[:accounts_count]

    async def delay(self):
        if len(self.settings.delay) == 1:
            await asyncio.sleep(self.settings.delay[0])
        else:
            await asyncio.sleep(
                random.randint(*self.settings.delay)
            )
