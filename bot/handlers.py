import logging
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, Any

from gptapi import yandex_gpt
from database_service_async import db_service

# Импортируем гибридный парсер и каталог
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from services.hybrid_parser import hybrid_parser
from services.catalog_service import catalog_service, CatalogService

logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

class MarkupState(StatesGroup):
    """Состояния для управления наценкой"""
    waiting_for_markup = State()

class CatalogStates(StatesGroup):
    """Состояния для каталога"""
    waiting_for_brand = State()

# Глобальные переменные для хранения данных каталога
catalog_data = {}
current_catalog_message = None

# Создаем reply клавиатуру
def get_main_keyboard():
    """Создает главную reply клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Каталог"), KeyboardButton(text="🗑️ Очистить БД")],
            [KeyboardButton(text="💰 Наценка"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_markup_keyboard():
    """Создает inline клавиатуру для выбора наценки"""
    markup_values = [100, 200, 300, 400, 500, 600, 700, 800, 900]
    buttons = []

    # Создаем кнопки по 3 в ряд
    for i in range(0, len(markup_values), 3):
        row = []
        for j in range(3):
            if i + j < len(markup_values):
                value = markup_values[i + j]
                row.append(InlineKeyboardButton(
                    text=f"{value}₽",
                    callback_data=f"markup_{value}"
                ))
        buttons.append(row)

    # Добавляем кнопку отмены
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="markup_cancel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для парсинга прайсов.\n\n"
        "Отправь мне текст с прайсами, и я автоматически их распарсю и сохраню в базу данных.\n\n"
        "Используй кнопки ниже для навигации:",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Бот для парсинга прайсов</b>

<b>Как использовать:</b>
1. Отправь мне текст с прайсами
2. Я автоматически распарсю их с помощью ИИ
3. Сохраню в базу данных только лучшие цены

<b>Команды:</b>
/start - Главное меню
/help - Эта справка
/catalog - Открыть каталог
/clear - Очистить базу данных

<b>Поддерживаемые форматы прайсов:</b>
• iPhone 13 128GB Midnight 🇺🇸 — 36900₽
• AirPods Max 2024 Purple — 39000₽
• MacBook Air M3 8/256GB Gray — 69000₽
• DualSense PS5 Black — 5300₽

<b>Особенности:</b>
• Автоматическое определение бренда, модели, конфигурации
• Сохранение только лучших цен
• Удобный каталог с фильтрацией
• Поддержка флагов стран
"""

    await message.answer(help_text, parse_mode="HTML")

@router.message(F.text == "📋 Каталог")
async def handle_catalog_button(message: Message, state: FSMContext):
    """Обработчик кнопки Каталог"""
    await show_catalog(message, state)

@router.message(F.text == "🗑️ Очистить БД")
async def handle_clear_db_button(message: Message):
    """Обработчик кнопки Очистить БД"""
    try:
        count = await db_service.clear_database()
        await message.answer(
            f"🗑️ База данных очищена!\n\nУдалено товаров: {count}",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка очистки БД: {e}")
        await message.answer("❌ Ошибка очистки базы данных", reply_markup=get_main_keyboard())

@router.message(F.text == "ℹ️ Помощь")
async def handle_help_button(message: Message):
    """Обработчик кнопки Помощь"""
    await cmd_help(message)

@router.message(F.text == "💰 Наценка")
async def handle_markup_button(message: Message, state: FSMContext):
    """Обработчик кнопки 'Наценка'"""
    try:
        current_markup = await db_service.get_current_markup()

        markup_text = f"💰 <b>Управление наценкой</b>\n\n"
        markup_text += f"Текущая наценка: <b>{current_markup:,.0f}₽</b>\n\n"
        markup_text += "Выберите новую наценку или введите сумму вручную:"

        await message.answer(
            markup_text,
            reply_markup=get_markup_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(MarkupState.waiting_for_markup)
    except Exception as e:
        logger.error(f"Ошибка показа наценки: {e}")
        await message.answer("❌ Ошибка получения данных о наценке", reply_markup=get_main_keyboard())

@router.message(MarkupState.waiting_for_markup)
async def handle_manual_markup_input(message: Message, state: FSMContext):
    """Обработчик ручного ввода наценки"""
    try:
        # Проверяем, что введено число
        try:
            markup_value = int(message.text.strip())
            if markup_value < 0:
                await message.answer("❌ Наценка не может быть отрицательной. Попробуйте еще раз:")
                return
        except ValueError:
            await message.answer("❌ Пожалуйста, введите число (например: 500):")
            return

        # Сохраняем в БД
        success = await db_service.set_markup(markup_value)

        if success:
            await message.answer(
                f"✅ <b>Наценка установлена!</b>\n\nНовая наценка: <b>{markup_value:,}₽</b>\n\n"
                f"Теперь все цены в каталоге будут отображаться с учетом наценки.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка сохранения наценки", reply_markup=get_main_keyboard())

        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка обработки ручного ввода наценки: {e}")
        await message.answer("❌ Ошибка установки наценки", reply_markup=get_main_keyboard())
        await state.clear()

@router.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений с прайсами - новая гибридная система"""
    try:
        # Показываем, что бот обрабатывает сообщение
        processing_msg = await message.answer("🔄 Анализирую прайсы с помощью умных шаблонов...")

        # Используем новую гибридную систему
        results = await hybrid_parser.parse_message(message.text, f"Пользователь {message.from_user.id}")

        if results['total_saved'] > 0:
            # Формируем детальный отчет
            report = f"🎉 **Успешно обработано!**\n\n{results['summary']}\n\n"
            report += "Данные сохранены в базу. Используйте кнопку '📋 Каталог' для просмотра."
            
            await processing_msg.edit_text(report, parse_mode="Markdown")
            await message.answer("Используйте кнопки ниже для навигации:", reply_markup=get_main_keyboard())
        else:
            await processing_msg.edit_text(
                "⚠️ Не удалось распознать прайсы в сообщении.\n\n"
                "Убедитесь, что сообщение содержит:\n"
                "• Модель устройства (iPhone 16, iPad Pro, etc.)\n"
                "• Объем памяти (128GB, 256GB, etc.)\n"
                "• Цвет\n"
                "• Флаг страны 🇺🇸🇯🇵🇮🇳\n"
                "• Цену в рублях"
            )
            await message.answer("Используйте кнопки ниже для навигации:", reply_markup=get_main_keyboard())

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке прайсов. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

async def show_catalog(message_or_callback, state: FSMContext):
    """Показывает каталог - выбор бренда"""
    try:
        global catalog_data, current_catalog_message

        # ПРИНУДИТЕЛЬНО получаем свежие данные каталога (без кеша)
        catalog_data = await catalog_service.get_catalog_data()

        if not catalog_data:
            text = "📋 Каталог пуст.\n\nОтправьте прайсы для заполнения каталога."
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
            ])

            if hasattr(message_or_callback, 'message'):  # CallbackQuery
                await message_or_callback.message.edit_text(text, reply_markup=keyboard)
            else:  # Message
                await message_or_callback.answer(text, reply_markup=keyboard)
            return

        # Создаем клавиатуру с брендами
        keyboard_buttons = []
        for brand_name in sorted(catalog_data.keys()):
            if brand_name != 'Unknown':  # Скрываем Unknown бренд
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"🏷️ {brand_name}", 
                    callback_data=f"brand_{brand_name}"
                )])

        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        text = "📋 <b>Каталог товаров</b>\n\nВыберите бренд:"

        if hasattr(message_or_callback, 'message'):  # CallbackQuery
            await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            current_catalog_message = message_or_callback.message
        else:  # Message
            msg = await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="HTML")
            current_catalog_message = msg

        await state.set_state(CatalogStates.waiting_for_brand)

    except Exception as e:
        logger.error(f"Ошибка показа каталога: {e}")
        if hasattr(message_or_callback, 'answer'):  # CallbackQuery
            await message_or_callback.answer("❌ Ошибка загрузки каталога")
        else:  # Message
            await message_or_callback.answer("❌ Ошибка загрузки каталога", reply_markup=get_main_keyboard())

@router.callback_query(F.data == "catalog")
async def show_catalog_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback для каталога"""
    await show_catalog(callback, state)

@router.callback_query(F.data.startswith("brand_"))
async def show_categories(callback: CallbackQuery, state: FSMContext):
    """Показывает категории выбранного бренда"""
    try:
        brand = callback.data.replace("brand_", "")
        
        if not catalog_data or brand not in catalog_data:
            await callback.answer("❌ Бренд не найден")
            return
        
        brand_data = catalog_data[brand]
        
        # Создаем клавиатуру с категориями
        keyboard_buttons = []
        for category_name in sorted(brand_data.keys()):
            # Определяем эмодзи для категорий
            emoji = "📱"
            if "iPad" in category_name:
                emoji = "📱"
            elif "MacBook" in category_name or "Mac" in category_name:
                emoji = "💻"
            elif "AirPods" in category_name:
                emoji = "🎧"
            elif "Watch" in category_name:
                emoji = "⌚"
            
            # Для Apple показываем только основные категории
            if brand == "Apple":
                if category_name in ["iPhone", "MacBook", "iPad", "AirPods", "Apple Watch"]:
                    keyboard_buttons.append([InlineKeyboardButton(
                        text=f"{emoji} {category_name}", 
                        callback_data=f"category_{brand}_{category_name}"
                    )])
            else:
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{emoji} {category_name}", 
                    callback_data=f"category_{brand}_{category_name}"
                )])

        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к брендам", callback_data="catalog")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        text = f"🏷️ <b>{brand}</b>\n\nВыберите категорию:"

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка показа категорий: {e}")
        await callback.answer("❌ Ошибка загрузки категорий")

@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery, state: FSMContext):
    """Показывает товары выбранной категории"""
    try:
        # Парсим callback_data: category_Apple_iPhone
        parts = callback.data.replace("category_", "").split("_", 1)
        if len(parts) != 2:
            await callback.answer("❌ Неверный формат данных")
            return
            
        brand, category = parts
        
        if not catalog_data or brand not in catalog_data or category not in catalog_data[brand]:
            await callback.answer("❌ Категория не найдена")
            return
        
        category_data = catalog_data[brand][category]
        
        # Если это iPhone - показываем поколения
        if category == "iPhone":
            await show_iphone_generations(callback, brand, category_data)
        elif category == "MacBook":
            await show_macbook_categories(callback, brand, category_data)
        elif category == "iPad":
            await show_ipad_categories(callback, brand, category_data)
        elif category == "Apple Watch":
            await show_apple_watch_categories(callback, brand, category_data)
        else:
            # For other categories - show items directly
            await show_category_products(callback, brand, category, category_data)
        
    except Exception as e:
        logger.error(f"Ошибка показа товаров категории: {e}")
        await callback.answer("❌ Ошибка загрузки товаров")

async def show_iphone_generations(callback, brand, iphone_list):
    """Показывает поколения iPhone"""
    try:
        # Группируем по поколениям
        generations = {}
        for phone in iphone_list:
            name = phone['name']
            if 'iPhone 16E' in name or name.endswith('16Е'):
                generation = '16E'
            elif 'iPhone 16Pro Max' in name:
                generation = '16'
            elif 'iPhone 16Pro' in name:
                generation = '16'
            elif 'iPhone 16Plus' in name:
                generation = '16'
            elif 'iPhone 16' in name:
                generation = '16'
            elif 'iPhone 15' in name:
                generation = '15'
            elif 'iPhone 14' in name:
                generation = '14'
            elif 'iPhone 13' in name:
                generation = '13'
            else:
                generation = 'Другие'
            
            if generation not in generations:
                generations[generation] = []
            generations[generation].append(phone)
        
        # Создаем клавиатуру с поколениями
        keyboard_buttons = []
        for generation in sorted(generations.keys()):
            if generation != 'Другие':
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"📱 iPhone {generation}", 
                    callback_data=f"generation_{generation}"
                )])
        
        if 'Другие' in generations:
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📱 Другие iPhone", 
                callback_data=f"generation_Другие"
            )])

        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"brand_{brand}")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        text = f"📱 <b>{brand} - iPhone</b>\n\nВыберите поколение:"

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка показа поколений iPhone: {e}")
        await callback.answer("❌ Ошибка загрузки поколений")

async def show_macbook_categories(callback, brand, macbook_data):
    """Показывает категории MacBook (Air, Pro, iMac)"""
    try:
        keyboard_buttons = []
        
        # Группируем по вариантам (Air, Pro, iMac)
        variants = {}
        for macbook in macbook_data:
            variant = macbook.get('variant', 'Air')
            if variant not in variants:
                variants[variant] = []
            variants[variant].append(macbook)
        
        # Сортируем варианты в нужном порядке
        variant_order = ['Air', 'Pro', 'iMac']
        for variant_name in variant_order:
            if variant_name in variants:
                emoji = "💻"
                if variant_name == "Air":
                    emoji = "💻"
                elif variant_name == "Pro":
                    emoji = "💻"
                elif variant_name == "iMac":
                    emoji = "🖥️"
                
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{emoji} MacBook {variant_name}",
                    callback_data=f"macbook_{variant_name}"
                )])
        
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"brand_{brand}")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        text = f"💻 <b>{brand} - MacBook</b>\n\nВыберите категорию:"
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка показа категорий MacBook: {e}")
        await callback.answer("❌ Ошибка загрузки категорий")

async def show_category_products(callback, brand, category, products):
    """Показывает товары категории (для iPad, MacBook, etc.)"""
    try:
        # Получаем текущую наценку
        current_markup = await catalog_service.get_current_markup()
        
        # Формируем сообщение с товарами
        emoji = "📱"
        if "iPad" in category:
            emoji = "📱"
        elif "MacBook" in category or "Mac" in category:
            emoji = "💻"
        elif "AirPods" in category:
            emoji = "🎧"
        elif "Watch" in category:
            emoji = "⌚"
            
        message_text = f"{emoji} <b>{brand} - {category}</b>\n\n"
        
        for product in products:
            config = product.get('configuration', '')
            if config:
                message_text += f"  {product['country']} {config} — <b>{product['display_price']:,}₽</b>\n"
            else:
                message_text += f"  {product['country']} {product['name']} — <b>{product['display_price']:,}₽</b>\n"
        
        # Создаем клавиатуру для возврата
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"brand_{brand}")]
        ])
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка показа товаров категории: {e}")
        await callback.answer("❌ Ошибка загрузки товаров")

@router.callback_query(F.data.startswith("generation_"))
async def show_generation_phones(callback: CallbackQuery, state: FSMContext):
    """Показывает iPhone выбранного поколения"""
    try:
        generation = callback.data.replace("generation_", "")
        
        if not catalog_data or 'Apple' not in catalog_data or 'iPhone' not in catalog_data['Apple']:
            await callback.answer("❌ Каталог не найден")
            return
        
        # iPhone каталог - это список, фильтруем по поколению
        iphone_list = catalog_data['Apple']['iPhone']
        
        # Фильтруем iPhone по поколению
        phones = []
        for phone in iphone_list:
            name = phone['name']
            phone_generation = None
            
            if generation == '16E' and ('iPhone 16E' in name or name.endswith('16Е')):
                phone_generation = '16E'
            elif generation == '16':
                if ('iPhone 16' in name and 'iPhone 16E' not in name) or 'iPhone 16Pro' in name or 'iPhone 16Plus' in name:
                    phone_generation = '16'
            elif f'iPhone {generation}' in name:
                phone_generation = generation
            elif generation == 'Другие':
                # Все остальные iPhone
                if not any(f'iPhone {g}' in name for g in ['13', '14', '15', '16']) and 'iPhone 16E' not in name:
                    phone_generation = 'Другие'
            
            if phone_generation == generation:
                phones.append(phone)
        
        if not phones:
            await callback.answer("❌ Товары не найдены")
            return
        
        # Формируем сообщение с прайсами
        message_text = f"📱 <b>iPhone {generation}</b>\n\n"
        
        # Группируем по типам (обычный, Pro, Plus, Pro Max)
        variants = {}
        for phone in phones:
            name = phone['name']
            
            # Определяем тип
            if 'Pro Max' in name:
                variant = 'Pro Max'
            elif 'Pro' in name:
                variant = 'Pro'
            elif 'Plus' in name:
                variant = 'Plus'
            elif generation == '16E':
                variant = 'E'
            else:
                variant = 'обычный'
            
            if variant not in variants:
                variants[variant] = []
            variants[variant].append(phone)
        
        # Выводим по вариантам
        for variant_name, variant_phones in variants.items():
            if variant_name == "обычный":
                message_text += f"<b>iPhone {generation}:</b>\n"
            elif variant_name == "E":
                message_text += f"<b>iPhone {generation}E:</b>\n"
            else:
                message_text += f"<b>iPhone {generation} {variant_name}:</b>\n"
            
            # Группируем по памяти (только GB, без цвета)
            memory_groups = {}
            for phone in variant_phones:
                config = phone.get('configuration', '')
                if not config:
                    # Если конфигурация в названии
                    clean_name = phone['name'].replace(f'iPhone {generation}', '').replace('iPhone', '').strip()
                    if variant_name != 'обычный' and variant_name in clean_name:
                        clean_name = clean_name.replace(variant_name, '').strip()
                    config = clean_name
                
                # Извлекаем только память (128GB, 256GB, 512GB, etc.)
                import re
                memory_match = re.search(r'(\d+GB)', config)
                if memory_match:
                    memory = memory_match.group(1)
                else:
                    memory = config  # Если не нашли GB, используем всю конфигурацию
                
                if memory not in memory_groups:
                    memory_groups[memory] = []
                memory_groups[memory].append(phone)
            
            # Выводим товары по группам памяти
            for memory, memory_phones in memory_groups.items():
                # Сортируем по странам внутри группы памяти
                memory_phones.sort(key=lambda x: x['country'])
                
                for phone in memory_phones:
                    config = phone.get('configuration', '')
                    # Формируем название iPhone с вариантом
                    iphone_name = f"iPhone {generation}"
                    if variant_name != 'обычный':
                        iphone_name += f" {variant_name}"
                    message_text += f"   {iphone_name} {config} — <b>{phone['display_price']:,}₽</b>{phone['country']}\n"
                message_text += "\n"  # Пустая строка между группами памяти
            
            message_text += "\n"  # Пустая строка между вариантами
        
        # Создаем клавиатуру для возврата
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к поколениям", callback_data="category_Apple_iPhone")]
        ])
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка показа поколения iPhone: {e}")
        await callback.answer("❌ Ошибка загрузки данных")

@router.callback_query(F.data.startswith("macbook_"))
async def show_macbook_products(callback: CallbackQuery, state: FSMContext):
    """Показывает товары MacBook выбранной категории"""
    try:
        variant = callback.data.replace("macbook_", "")
        if not catalog_data or 'Apple' not in catalog_data or 'MacBook' not in catalog_data['Apple']:
            await callback.answer("❌ Каталог не найден")
            return
        
        macbook_list = catalog_data['Apple']['MacBook']
        products = []
        for macbook in macbook_list:
            macbook_variant = macbook.get('variant', 'Air')
            if macbook_variant == variant:
                products.append(macbook)
        
        if not products:
            await callback.answer("❌ Товары не найдены")
            return
        
        # Группируем по размеру экрана и чипу (13 M1, 13 M2, 15 M4, etc.)
        size_chip_groups = {}
        for product in products:
            generation = product.get('generation', '')
            size = product.get('size', '')
            
            # Извлекаем чип из поколения (M1, M2, M3, M4)
            import re
            chip_match = re.search(r'(M\d+)', generation)
            if chip_match:
                chip = chip_match.group(1)
            else:
                chip = generation
            
            # Создаем ключ для группировки: размер + чип
            group_key = f"{size} {chip}" if size else chip
            
            if group_key not in size_chip_groups:
                size_chip_groups[group_key] = []
            size_chip_groups[group_key].append(product)
        
        message_text = f"💻 <b>MacBook {variant}</b>\n\n"
        
        # Сортируем группы по размеру и чипу
        def sort_key(item):
            key = item[0]
            # Извлекаем размер и чип для сортировки
            size_match = re.search(r'(\d+)', key)
            chip_match = re.search(r'(M\d+)', key)
            
            size = int(size_match.group(1)) if size_match else 0
            chip_num = int(chip_match.group(1)[1:]) if chip_match else 0
            
            return (size, chip_num)
        
        sorted_groups = sorted(size_chip_groups.items(), key=sort_key)
        
        # Выводим товары по группам
        for group_key, group_products in sorted_groups:
            # Группируем по памяти внутри группы
            memory_groups = {}
            for product in group_products:
                memory = product.get('memory', '')
                if not memory:
                    # Если память не указана, извлекаем из конфигурации
                    config = product.get('configuration', '')
                    memory_match = re.search(r'(\d+GB)', config)
                    memory = memory_match.group(1) if memory_match else '8GB'
                
                if memory not in memory_groups:
                    memory_groups[memory] = []
                memory_groups[memory].append(product)
            
            # Выводим группу
            message_text += f"<b>MacBook {variant} {group_key}</b>\n"
            
            # Сортируем группы памяти по значению
            sorted_memory_groups = sorted(memory_groups.items(), key=lambda item: int(re.search(r'(\d+)', item[0]).group(1)) if re.search(r'(\d+)', item[0]) else 0)
            
            # Выводим товары по группам памяти
            for memory, memory_products in sorted_memory_groups:
                # Группируем по размеру диска внутри группы памяти
                storage_groups = {}
                for product in memory_products:
                    storage = product.get('storage', '')
                    if not storage:
                        # Если размер диска не указан, извлекаем из конфигурации
                        config = product.get('configuration', '')
                        storage_match = re.search(r'(\d+GB)', config)
                        if storage_match:
                            storage = storage_match.group(1)
                        else:
                            # Ищем второй GB в конфигурации (первый - память, второй - диск)
                            gb_matches = re.findall(r'(\d+GB)', config)
                            if len(gb_matches) > 1:
                                storage = gb_matches[1]
                            else:
                                storage = '256GB'  # По умолчанию
                    
                    if storage not in storage_groups:
                        storage_groups[storage] = []
                    storage_groups[storage].append(product)
                
                # Сортируем группы диска по значению
                sorted_storage_groups = sorted(storage_groups.items(), key=lambda item: int(re.search(r'(\d+)', item[0]).group(1)) if re.search(r'(\d+)', item[0]) else 0)
                
                # Выводим товары по группам диска
                for storage, storage_products in sorted_storage_groups:
                    # Сортируем по странам внутри группы диска
                    storage_products.sort(key=lambda x: x['country'] or '')
                    
                    for product in storage_products:
                        config = product.get('configuration', '')
                        product_code = product.get('product_code', '')
                        country = product.get('country', '')
                        final_price = product['display_price']
                        
                        # Убираем дублирование памяти из конфигурации
                        # Если конфигурация содержит дублированную память (например "16GB 16GB 256GB"), исправляем
                        import re
                        config_cleaned = re.sub(r'(\d+GB)\s+\1\s+', r'\1 ', config)
                        
                        # Формируем строку: флаг + код + конфигурация
                        if country:
                            if product_code:
                                message_text += f"  {country} {product_code} {config_cleaned} — <b>{final_price:,}₽</b>\n"
                            else:
                                message_text += f"  {country} {config_cleaned} — <b>{final_price:,}₽</b>\n"
                        else:
                            if product_code:
                                message_text += f"  {product_code} {config_cleaned} — <b>{final_price:,}₽</b>\n"
                            else:
                                message_text += f"  {config_cleaned} — <b>{final_price:,}₽</b>\n"
                    message_text += "\n"  # Пустая строка между группами памяти
            
            message_text += "\n"  # Пустая строка между группами
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="category_Apple_MacBook")]
        ])
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка показа товаров MacBook: {e}")
        await callback.answer("❌ Ошибка загрузки данных")

async def show_ipad_categories(callback, brand, ipad_data):
    """Показывает категории iPad"""
    try:
        if not ipad_data:
            await callback.answer("❌ Нет данных iPad")
            return
        
        # Группируем по типам iPad
        categories = {}
        for ipad in ipad_data:
            variant = ipad.get('variant', '')
            generation = ipad.get('generation', '')
            
            # Определяем категорию на основе variant и generation
            if variant == 'Mini':
                category = 'Mini'
            elif variant == 'Air':
                category = 'Air'
            elif variant == 'Pro':
                category = 'Pro'
            elif generation and generation.isdigit():
                # Если generation - это число (9, 10, 11), то это обычный iPad
                category = 'iPad'
            else:
                # По умолчанию обычный iPad
                category = 'iPad'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(ipad)
        
        # Создаем кнопки для категорий
        buttons = []
        for category, products in categories.items():
            if category == 'iPad':
                display_name = 'iPad'
            else:
                display_name = f'iPad {category}'
            buttons.append([InlineKeyboardButton(
                text=f"📱 {display_name}",
                callback_data=f"ipad_{category}"
            )])
        
        # Добавляем кнопку "Назад"
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="brand_Apple")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            "📱 Выберите категорию iPad:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка показа категорий iPad: {e}")
        await callback.answer("❌ Ошибка загрузки данных")

@router.callback_query(F.data.startswith("ipad_"))
async def show_ipad_products(callback: CallbackQuery, state: FSMContext):
    """Показывает товары iPad выбранной категории"""
    try:
        variant = callback.data.replace("ipad_", "")
        if not catalog_data or 'Apple' not in catalog_data or 'iPad' not in catalog_data['Apple']:
            await callback.answer("❌ Каталог не найден")
            return
        
        ipad_list = catalog_data['Apple']['iPad']
        products = []
        for ipad in ipad_list:
            ipad_variant = ipad.get('variant', '')
            ipad_generation = ipad.get('generation', '')
            
            # Определяем категорию iPad
            if ipad_variant == 'Mini':
                ipad_category = 'Mini'
            elif ipad_variant == 'Air':
                ipad_category = 'Air'
            elif ipad_variant == 'Pro':
                ipad_category = 'Pro'
            elif ipad_generation and ipad_generation.isdigit():
                ipad_category = 'iPad'
            else:
                ipad_category = 'iPad'
            
            # Если категория совпадает с выбранной
            if ipad_category == variant:
                products.append(ipad)
        
        if not products:
            await callback.answer("❌ Товары не найдены")
            return
        
        # Группируем по размеру и поколению
        groups = {}
        for product in products:
            size = product.get('size', '')
            generation = product.get('generation', '')
            variant_name = product.get('variant', '')
            
            # Формируем название группы
            if variant_name == 'Mini':
                group_key = f"iPad Mini {size}"
            elif variant_name == 'Air':
                group_key = f"iPad Air {size}"
            elif variant_name == 'Pro':
                group_key = f"iPad Pro {size}"
            elif generation and generation.isdigit():
                group_key = f"iPad {generation}"
            else:
                group_key = f"iPad {size}" if size else "iPad"
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(product)
        
        # Сортируем группы
        sorted_groups = sorted(groups.items(), key=lambda x: x[0])
        
        # Формируем заголовок
        if variant == 'iPad':
            message_text = "📱 iPad\n\n"
        else:
            message_text = f"📱 iPad {variant}\n\n"
        
        for group_name, group_products in sorted_groups:
            message_text += f"<b>{group_name}</b>\n"
            
            # Группируем по объему памяти внутри группы
            memory_groups = {}
            for product in group_products:
                storage = product.get('storage', '')
                if not storage:
                    storage = '128GB'  # По умолчанию
                
                if storage not in memory_groups:
                    memory_groups[storage] = []
                memory_groups[storage].append(product)
            
            # Сортируем группы памяти по значению
            sorted_memory_groups = sorted(memory_groups.items(), key=lambda item: int(re.search(r'(\d+)', item[0]).group(1)) if re.search(r'(\d+)', item[0]) else 0)
            
            # Выводим товары по группам памяти
            for storage, storage_products in sorted_memory_groups:
                # Сортируем по странам внутри группы памяти
                storage_products.sort(key=lambda x: x['country'] or '')
                
                for product in storage_products:
                    config = product.get('configuration', '')
                    product_code = product.get('product_code', '')
                    country = product.get('country', '')
                    final_price = product['display_price']
                    
                    # Формируем строку: флаг + код + конфигурация
                    if country:
                        if product_code:
                            message_text += f"  {country} {product_code} {config} — <b>{final_price:,}₽</b>\n"
                        else:
                            message_text += f"  {country} {config} — <b>{final_price:,}₽</b>\n"
                    else:
                        if product_code:
                            message_text += f"  {product_code} {config} — <b>{final_price:,}₽</b>\n"
                        else:
                            message_text += f"  {config} — <b>{final_price:,}₽</b>\n"
                message_text += "\n"  # Пустая строка между группами памяти
            
            message_text += "\n"  # Пустая строка между группами
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="category_Apple_iPad")]
        ])
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка показа товаров iPad: {e}")
        await callback.answer("❌ Ошибка загрузки данных")

@router.callback_query(F.data == "clear_db")
async def clear_database(callback: CallbackQuery):
    """Очищает базу данных"""
    try:
        count = await db_service.clear_database()

        await callback.message.edit_text(
            f"🗑️ База данных очищена!\n\nУдалено товаров: {count}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
            ])
        )

    except Exception as e:
        logger.error(f"Ошибка очистки БД: {e}")
        await callback.answer("❌ Ошибка очистки базы данных")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    try:
        await state.clear()

        # Отправляем новое сообщение с reply клавиатурой
        await callback.message.answer(
            "🤖 <b>Главное меню</b>\n\n"
            "Отправь мне текст с прайсами, и я автоматически их распарсю и сохраню в базу данных.\n\n"
            "Используй кнопки ниже для навигации:",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

        # Удаляем старое сообщение
        await callback.message.delete()

    except Exception as e:
        logger.error(f"Ошибка возврата в главное меню: {e}")
        await callback.answer("❌ Ошибка")

# Обработчики команд
@router.message(Command("catalog"))
async def cmd_catalog(message: Message, state: FSMContext):
    """Команда для открытия каталога"""
    await show_catalog(message, state)

@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Команда для очистки базы данных"""
    try:
        count = await db_service.clear_database()
        await message.answer(f"🗑️ База данных очищена! Удалено товаров: {count}", reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка очистки БД: {e}")
        await message.answer("❌ Ошибка очистки базы данных", reply_markup=get_main_keyboard())

@router.callback_query(F.data.startswith("markup_"))
async def handle_markup_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик inline кнопок наценки"""
    try:
        if callback.data == "markup_cancel":
            await callback.message.edit_text("❌ Изменение наценки отменено")
            await state.clear()
            await callback.answer()
            return
        
        # Извлекаем значение наценки
        markup_value = int(callback.data.replace("markup_", ""))
        
        # Сохраняем в БД
        success = await db_service.set_markup(markup_value)
        
        if success:
            await callback.message.edit_text(
                f"✅ <b>Наценка установлена!</b>\n\nНовая наценка: <b>{markup_value:,}₽</b>\n\n"
                f"Теперь все цены в каталоге будут отображаться с учетом наценки.",
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text("❌ Ошибка сохранения наценки")
        
        await state.clear()
        await callback.answer(f"✅ Наценка {markup_value}₽ установлена!")
    except Exception as e:
        logger.error(f"Ошибка обработки callback наценки: {e}")
        await callback.answer("❌ Ошибка установки наценки")

async def show_apple_watch_categories(callback, brand, apple_watch_data):
    """Показывает категории Apple Watch"""
    try:
        # Группируем по сериям
        categories = {}
        for watch in apple_watch_data:
            series = watch.get('series', '')
            if not series:
                continue
                
            if series not in categories:
                categories[series] = []
            categories[series].append(watch)
        
        if not categories:
            await callback.message.edit_text("❌ Apple Watch не найдены")
            return
        
        # Создаем кнопки для категорий
        buttons = []
        for series, products in categories.items():
            display_name = f'Apple Watch {series}'
            buttons.append([InlineKeyboardButton(
                text=f"⌚ {display_name}",
                callback_data=f"apple_watch_{series}"
            )])
        
        # Добавляем кнопку "Назад"
        buttons.append([InlineKeyboardButton(
            text="🔙 Назад к брендам",
            callback_data="show_brands"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            "⌚ <b>Apple Watch</b>\n\nВыберите серию:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка показа категорий Apple Watch: {e}")
        await callback.answer("❌ Ошибка загрузки категорий")

@router.callback_query(F.data.startswith("apple_watch_"))
async def show_apple_watch_products(callback: CallbackQuery, state: FSMContext):
    """Показывает товары Apple Watch выбранной серии"""
    try:
        series = callback.data.replace("apple_watch_", "")
        
        # Получаем данные каталога
        catalog_service = CatalogService()
        catalog_data = await catalog_service.get_catalog_data()
        
        if 'Apple' not in catalog_data or 'Apple Watch' not in catalog_data['Apple']:
            await callback.answer("❌ Apple Watch не найдены")
            return
        
        apple_watch_list = catalog_data['Apple']['Apple Watch']
        products = []
        
        for watch in apple_watch_list:
            watch_series = watch.get('series', '')
            
            # Если серия совпадает с выбранной
            if watch_series == series:
                products.append(watch)
        
        if not products:
            await callback.answer("❌ Товары не найдены")
            return
        
        # Группируем по размерам
        size_groups = {}
        for product in products:
            size = product.get('size', '')
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(product)
        
        # Формируем сообщение
        message_text = f"⌚ <b>Apple Watch {series}</b>\n\n"
        
        for size, size_products in sorted(size_groups.items()):
            if size:
                message_text += f"<b>📏 {size}mm</b>\n"
            
            # Сортируем по цвету корпуса
            size_products.sort(key=lambda x: x.get('case_color', ''))
            
            for product in size_products:
                country = product.get('country', '')
                product_code = product.get('product_code', '')
                config = product.get('configuration', '')
                final_price = product.get('display_price', 0)
                
                # Формируем строку: флаг код конфигурация — цена
                if product_code:
                    message_text += f"  {country} {product_code} {config} — <b>{final_price:,}₽</b>\n"
                else:
                    message_text += f"  {country} {config} — <b>{final_price:,}₽</b>\n"
            
            message_text += "\n"
        
        # Создаем кнопки
        buttons = [[InlineKeyboardButton(
            text="🔙 Назад к Apple Watch",
            callback_data="show_category_Apple_Apple Watch"
        )]]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка показа товаров Apple Watch: {e}")
        await callback.answer("❌ Ошибка загрузки товаров")