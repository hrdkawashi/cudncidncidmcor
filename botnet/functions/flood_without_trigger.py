import asyncio
from functions.base import TelethonFunction
from functions.flood import Flood
from rich.console import Console

console = Console()


class FloodWithoutTriggerFunc(TelethonFunction):
    """Спам без триггеров(asyncio)"""

    async def execute(self):
        link = console.input("[bold red]Ссылка> [/]")
        flood = Flood(self.storage, self.settings)
        flood.ask()

        await asyncio.gather(*[
            flood.flood(session, link, flood.function)
            for session in self.sessions
        ])
        