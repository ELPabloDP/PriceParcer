import telethon
import logging
import re
import json
import asyncio
import redis_publisher, utils


logger = logging.getLogger(__name__)

API_ID = 18463571
API_HASH = "fbef9db453a528c2648220730edbff50"
SESSION_NAME = "89004924269"


class TelethonParser:
    def __init__(self, session_name: str, api_id: int, api_hash: str):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = telethon.TelegramClient(session_name, api_id, api_hash, device_model="iPhone 12 Pro", system_version="4.16.30-CUSTOM")


    async def start(self):
        await self.client.start()

    async def stop(self):
        await self.client.disconnect()

    async def parse_message(self, message: telethon.types.Message):
        pass


if __name__ == "__main__":
    parser = TelethonParser(SESSION_NAME, API_ID, API_HASH)
    asyncio.run(parser.start())
    asyncio.run(parser.stop())

