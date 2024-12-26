import asyncio
import random
import os

from telethon import TelegramClient, functions

from rich.progress import track
from rich.console import Console

from functions.base import TelethonFunction
console = Console()


class ChangeProfilePhotoFunc(TelethonFunction):
    """Изменение аватара"""
    
    async def set_profile_photo(self, session: TelegramClient, photo_path: str):
        async with self.storage.ainitialize_session(session):
            me = await session.get_me()

            try:
                await session(functions.photos.UploadProfilePhotoRequest(
                    file=await session.upload_file(photo_path),
                ))
            except Exception as err:
                console.print(
                    "[{name}] [bold red]Ошибка[/] : {err}"
                    .format(name=me.first_name, error=err)
                )
            else:
                console.print(
                    "[{name}] Фотография успешно загружена [bold green]успешно[/] ({photo_path})"
                    .format(name=me.first_name, photo_path=photo_path)
                )


    async def execute(self):
        path = os.path.join(os.getcwd(), "assets", "photos")
        console.input(
            f"\n[bold white]Будут использоваться фотографии из папки {path}"
            "\nНажмите [Enter] чтобы продолжить[/]"
        )
        
        photos = os.listdir(path)
        
        await asyncio.gather(*[
            self.set_profile_photo(session, os.path.join(path, random.choice(photos)))
            for session in self.sessions
        ])            