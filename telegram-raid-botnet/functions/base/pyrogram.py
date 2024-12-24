import struct
import base64

from typing import List
from pyrogram import Client
from telethon import TelegramClient

from modules.storages.sessions_storage import SessionsStorage
from modules.settings import Settings
from modules.types.json_session import JsonSession
from functions.base.base import BaseFunction


class PyrogramFunction(BaseFunction):
    PYROGRAM_STRING_SESSION_FORMAT = ">BI?256sQ?"

    def __init__(self, storage: SessionsStorage, settings: Settings):
        self.storage = storage
        self.settings = settings

        self.telethon_sessions: List[TelegramClient] = storage.sessions
        self.json_sessions: List[JsonSession] = storage.json_sessions
        self.sessions: List[Client] = []
        
        for json_session, session in zip(self.json_sessions, self.telethon_sessions):
            packed = struct.pack(
                self.PYROGRAM_STRING_SESSION_FORMAT,
                session.session.dc_id,
                settings.api_id,
                False,
                session.session.auth_key.key,
                111,
                False      
            )
            
            pyrogram_string_session = base64.urlsafe_b64encode(packed).decode().rstrip("=")

            self.sessions.append(
                Client(
                    name=self.storage.get_session_path(session),
                    api_id=json_session.account.application.api_id,
                    api_hash=json_session.account.application.api_hash,
                    session_string=pyrogram_string_session,
                    app_version=json_session.account.application.app_version,
                    device_model=json_session.account.application.device_name,
                    system_version=json_session.account.application.sdk,
                    lang_code=json_session.account.application.system_lang_code,
                    in_memory=True
                )
            )
