import asyncio
import json
import os
from contextlib import asynccontextmanager, contextmanager
from typing import Dict, List, Union

from rich.console import Console
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from modules.types.json_session import JsonSession

console = Console()

DEBUG_MODE = False  # Включить/выключить отладочные сообщения

class SessionsStorage:
    def __init__(self, directory: str, api_id: Union[str, int], api_hash: str):
        self.full_sessions: Dict[str, Union[TelegramClient, JsonSession]] = {}
        self.json_sessions: List[JsonSession] = []
        self.jsessions_paths: Dict[str, JsonSession] = {}

        self.initialize = True  # Статическое значение для автоматического запуска сессий

        for file in os.listdir(directory):
            if file.endswith(".session"):
                session_path = os.path.join(directory, file)

                with open(session_path) as fileobj:
                    auth_key = fileobj.read()

                if len(auth_key) != 353:
                    continue

                client = TelegramClient(
                    StringSession(auth_key),
                    api_id,
                    api_hash,
                    device_model="Redmi Note 10",
                    lang_code="en",
                    system_lang_code="en",
                )

                self.full_sessions[session_path] = client

            elif file.endswith(".jsession"):
                session_path = os.path.join(directory, file)

                with open(session_path) as fileobj:
                    session_settings = json.load(fileobj)

                session = JsonSession(dict_settings=session_settings)

                if old_session := self.is_phone_exists(
                    session.account.account.phone_number
                ):
                    old_session_path = self.get_json_session_path(old_session)

                    if DEBUG_MODE:
                        # Логирование отключено
                        pass

                    continue

                client = TelegramClient(
                    session=StringSession(session.account.auth_key),
                    api_id=session.account.application.api_id,
                    api_hash=session.account.application.api_hash,
                    device_model=session.account.application.device_name,
                    app_version=session.account.application.app_version,
                    system_version=session.account.application.sdk,
                    lang_code=session.account.application.system_lang_code,
                    system_lang_code=session.account.application.system_lang_code,
                    proxy=session.account.proxy.as_telethon()
                    if session.account.proxy else None,
                )

                self.full_sessions[session_path] = client
                self.json_sessions.append(session)
                self.jsessions_paths[session_path] = session

        if self.initialize:
            if len(self.full_sessions) == 0:
                return print(
                    "Для работы ботнета необходимо добавить аккаунты."
                )

            with console.status("Initializing..."):
                asyncio.get_event_loop().run_until_complete(
                    asyncio.gather(
                        *[
                            self.check_session(session, path)
                            for path, session in self.full_sessions.items()
                        ]
                    )
                )

    async def check_session(self, session: TelegramClient, path: str):
        # Логирование отключено
        try:
            await session.connect()
        except ConnectionError:
            json_session = self.jsessions_paths.get("path")
            
            if json_session is not None:
                if json_session.account.proxy is not None:
                    return  # Логирование отключено

            # Логирование отключено

        except Exception as err:
            # Логирование отключено
            del self.full_sessions[path]
            os.remove(path)
            return

        if not await session.is_user_authorized():
            # Логирование отключено
            del self.full_sessions[path]
            os.remove(path)
            return

        # Логирование отключено

    def get_session_path(self, session: TelegramClient | JsonSession) -> str:
        for path, client in self.full_sessions.items():
            if client == session:
                return path

    def get_json_session_path(self, json_session_: TelegramClient | JsonSession) -> str:
        for path, json_session in self.jsessions_paths.items():
            if json_session == json_session_:
                return path

    def is_phone_exists(self, phone: int) -> bool | JsonSession:
        for session in self.json_sessions:
            if session.account.account.phone_number == phone:
                return session

        return False

    @property
    def sessions(self) -> List[TelegramClient]:
        return list(self.full_sessions.values())

    @contextmanager
    def initialize_session(self, session):
        if not self.initialize:
            session.connect()

        yield

        if not self.initialize:
            session.disconnect()

    @asynccontextmanager
    async def ainitialize_session(self, session):
        if not self.initialize:
            await session.connect()

        yield

        if not self.initialize:
            await session.disconnect()

    def __len__(self):
        return len(self.sessions)