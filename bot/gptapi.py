import json
import logging
import os
import ssl
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class YandexGPTAPI:
    """Класс для работы с Яндекс GPT API"""
    
    def __init__(self):
        self.api_key = os.getenv("YANDEX_GPT_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        if not self.api_key or not self.folder_id:
            raise ValueError("Необходимо указать YANDEX_GPT_API_KEY и YANDEX_FOLDER_ID в .env файле")
    
    def split_text_into_chunks(self, text: str, max_length: int = 8000) -> List[str]:
        """Разбивает длинный текст на части"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 для символа новой строки
            
            if current_length + line_length > max_length and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    async def parse_prices(self, price_text: str, device_type: str = None) -> List[Dict[str, Any]]:
        """
        Парсит текст с прайсами и возвращает структурированный JSON
        
        Args:
            price_text: Текст с прайсами
            
        Returns:
            Список словарей с информацией о товарах
        """
        
        # Импортируем промпты
        from .prompts import get_prompt_for_device, BASE_PROMPT
        
        # Выбираем специализированный промпт или базовый
        if device_type:
            prompt_template = get_prompt_for_device(device_type)
        else:
            prompt_template = BASE_PROMPT
        
        prompt = f"{prompt_template}\n\nТекст с прайсами:\n{price_text}"

        try:
            # Создаем SSL контекст
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            logger.info(f"Отправляемый промпт: {prompt[:500]}...")
            async with aiohttp.ClientSession(connector=connector) as session:
                headers = {
                    "Authorization": f"Api-Key {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.1,
                        "maxTokens": 24000
                    },
                    "messages": [
                        {
                            "role": "user",
                            "text": prompt
                        }
                    ]
                }
                
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    logger.info(f"Статус ответа: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Полный ответ от API: {result}")
                        
                        if "result" not in result:
                            logger.error("Нет поля 'result' в ответе")
                            return []
                        
                        if "alternatives" not in result["result"]:
                            logger.error("Нет поля 'alternatives' в результате")
                            return []
                        
                        alternatives = result["result"]["alternatives"]
                        if not alternatives:
                            logger.error("Пустой массив alternatives")
                            return []
                        
                        if "message" not in alternatives[0]:
                            logger.error("Нет поля 'message' в альтернативе")
                            return []
                        
                        if "text" not in alternatives[0]["message"]:
                            logger.error("Нет поля 'text' в сообщении")
                            return []
                        
                        content = alternatives[0]["message"]["text"]
                        logger.info(f"Извлеченный текст: '{content}'")
                        
                        if not content.strip():
                            logger.error("Пустой ответ от GPT")
                            return []
                        
                        # Парсим JSON ответ
                        try:
                            # Убираем markdown блоки если есть
                            if content.startswith('```'):
                                lines = content.split('\n')
                                # Находим начало и конец JSON
                                start_idx = 0
                                end_idx = len(lines)
                                for i, line in enumerate(lines):
                                    if line.strip() == '```json' or line.strip() == '```':
                                        start_idx = i + 1
                                        break
                                for i in range(len(lines) - 1, -1, -1):
                                    if lines[i].strip() == '```':
                                        end_idx = i
                                        break
                                content = '\n'.join(lines[start_idx:end_idx])
                            
                            # Проверяем, что это не обычный текст
                            if not content.strip().startswith('[') and not content.strip().startswith('{'):
                                logger.error(f"GPT вернул не JSON: {content}")
                                return []
                            
                            # Исправляем проблемы с экранированием в JSON
                            import re
                            # Убираем лишние обратные слеши в конце строк
                            content = re.sub(r'([^\\])\\",\s*$', r'\1",', content, flags=re.MULTILINE)
                            content = re.sub(r'([^\\])\\"$', r'\1"', content, flags=re.MULTILINE)
                            # Исправляем проблемы с кавычками в размерах экранов
                            content = content.replace('\\"', 'inch')
                            
                            parsed_data = json.loads(content)
                            
                            # Фильтруем товары с валидными данными
                            valid_products = []
                            for product in parsed_data:
                                # Проверяем обязательные поля
                                if (product.get('firm') and 
                                    product.get('device') and 
                                    product.get('price') is not None and 
                                    product.get('price') > 0):
                                    valid_products.append(product)
                                else:
                                    logger.warning(f"Пропущен товар с неполными данными: {product}")
                            
                            logger.info(f"Успешно распарсено {len(valid_products)} товаров (отфильтровано {len(parsed_data) - len(valid_products)} невалидных)")
                            return valid_products
                        except json.JSONDecodeError as e:
                            logger.error(f"Ошибка парсинга JSON: {e}")
                            logger.error(f"Ответ от GPT: {content}")
                            return []
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка API: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Ошибка при обращении к Yandex GPT API: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Тестирует соединение с API"""
        try:
            test_prompt = "Привет, это тест соединения. Ответь 'OK'."
            result = await self.parse_prices(test_prompt)
            return len(result) >= 0  # Если не было ошибки, соединение работает
        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            return False

# Создаем глобальный экземпляр
yandex_gpt = YandexGPTAPI()
