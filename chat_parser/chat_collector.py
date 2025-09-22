#!/usr/bin/env python3
"""
Скрипт для сбора данных из всех чатов аккаунта
Собирает последние 5 сообщений из каждого чата/канала
"""

import asyncio
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
API_ID = 18463571
API_HASH = "fbef9db453a528c2648220730edbff50"
SESSION_NAME = "89004924269"

class ChatCollector:
    def __init__(self, session_name: str, api_id: int, api_hash: str):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient(
            session_name, 
            api_id, 
            api_hash, 
            device_model="iPhone 12 Pro", 
            system_version="4.16.30-CUSTOM"
        )
        self.collected_data = []

    async def start(self):
        """Запуск клиента"""
        await self.client.start()
        logger.info("Клиент запущен")

    async def stop(self):
        """Остановка клиента"""
        await self.client.disconnect()
        logger.info("Клиент остановлен")

    async def get_chat_info(self, chat):
        """Получение информации о чате"""
        try:
            if isinstance(chat, Channel):
                return {
                    "id": chat.id,
                    "title": chat.title,
                    "username": chat.username,
                    "type": "channel" if chat.broadcast else "supergroup",
                    "participants_count": getattr(chat, 'participants_count', 0),
                    "link": f"https://t.me/{chat.username}" if chat.username else None
                }
            elif isinstance(chat, Chat):
                return {
                    "id": chat.id,
                    "title": chat.title,
                    "type": "group",
                    "participants_count": getattr(chat, 'participants_count', 0),
                    "link": None
                }
            elif isinstance(chat, User):
                return {
                    "id": chat.id,
                    "title": f"{chat.first_name} {chat.last_name or ''}".strip(),
                    "username": chat.username,
                    "type": "private",
                    "participants_count": 1,
                    "link": f"https://t.me/{chat.username}" if chat.username else None
                }
        except Exception as e:
            logger.error(f"Ошибка получения информации о чате {chat.id}: {e}")
            return None

    async def get_last_messages(self, chat, limit=5):
        """Получение последних сообщений из чата"""
        try:
            messages = []
            async for message in self.client.iter_messages(chat, limit=limit):
                if message.text:  # Только текстовые сообщения
                    messages.append({
                        "id": message.id,
                        "text": message.text,
                        "date": message.date.isoformat() if message.date else None,
                        "sender_id": message.sender_id,
                        "reply_to_msg_id": message.reply_to_msg_id
                    })
            return messages
        except Exception as e:
            logger.error(f"Ошибка получения сообщений из чата {chat.id}: {e}")
            return []

    async def collect_all_chats(self):
        """Сбор данных из всех чатов"""
        logger.info("Начинаем сбор данных из чатов...")
        
        try:
            # Получаем все диалоги
            dialogs = await self.client.get_dialogs()
            logger.info(f"Найдено {len(dialogs)} диалогов")
            
            for i, dialog in enumerate(dialogs, 1):
                chat = dialog.entity
                logger.info(f"Обрабатываем чат {i}/{len(dialogs)}: {getattr(chat, 'title', 'Unknown')}")
                
                # Получаем информацию о чате
                chat_info = await self.get_chat_info(chat)
                if not chat_info:
                    continue
                
                # Получаем последние сообщения
                messages = await self.get_last_messages(chat, limit=5)
                
                # Сохраняем данные
                chat_data = {
                    "chat_info": chat_info,
                    "messages": messages,
                    "collected_at": datetime.now().isoformat()
                }
                
                self.collected_data.append(chat_data)
                logger.info(f"Собрано {len(messages)} сообщений из чата '{chat_info['title']}'")
                
                # Небольшая пауза между запросами
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Ошибка при сборе данных: {e}")

    async def save_data(self, filename="chat_data.json"):
        """Сохранение собранных данных в JSON файл"""
        try:
            output_data = {
                "collected_at": datetime.now().isoformat(),
                "total_chats": len(self.collected_data),
                "chats": self.collected_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Данные сохранены в файл: {filename}")
            logger.info(f"Всего чатов: {len(self.collected_data)}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")

    async def run(self):
        """Основной метод запуска"""
        try:
            await self.start()
            await self.collect_all_chats()
            await self.save_data()
        finally:
            await self.stop()

async def main():
    """Главная функция"""
    collector = ChatCollector(SESSION_NAME, API_ID, API_HASH)
    await collector.run()

if __name__ == "__main__":
    asyncio.run(main())
