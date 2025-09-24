#!/usr/bin/env python3
import sys
sys.path.append('.')

from parsers.macbook_parser import MacBookParser

def test_macbook_parser():
    """Тестирует MacBook парсер на всех MacBook строках из exampleprices.txt"""
    
    # Читаем файл с примерами цен
    try:
        with open('bot/exampleprices.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл bot/exampleprices.txt не найден!")
        return
    
    # Разбиваем на строки
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Фильтруем только MacBook строки
    macbook_lines = []
    for line in lines:
        line_lower = line.lower()
        # Должна содержать MacBook, Mac, Air, Pro и не быть iPhone, iPad, Watch и т.д.
        if any(keyword in line_lower for keyword in ['macbook', 'mac ', 'air', 'pro']) and not any(keyword in line_lower for keyword in [
            'iphone', 'ipad', 'watch', 'aw ', 'pixel', 'galaxy', 'dyson', 'pencil', 'airtag', 
            'adapter', 'magic', 'mouse', 'keyboard', 'google', 'samsung', 'airpods', 'pro max', 'pro 14', 'pro 15', 'pro 16',
            '13 pro', '14 pro', '15 pro', '16 pro', 'pro 128', 'pro 256', 'pro 512', 'pro 1tb', 'pro 2tb'
        ]):
            macbook_lines.append(line)
    
    print(f"💻 Найдено {len(macbook_lines)} MacBook строк для тестирования:")
    for i, line in enumerate(macbook_lines, 1):
        print(f"  {i:3d}. {line}")
    
    print(f"\n🧪 Тестируем MacBook парсер:")
    
    # Создаем парсер
    macbook_parser = MacBookParser()
    
    # Тестируем каждую строку
    parsed_count = 0
    unparsed_lines = []
    
    for i, line in enumerate(macbook_lines, 1):
        result = macbook_parser._parse_single_line(line, [], 0)
        if result:
            print(f"  ✅ {i:3d}. {line}")
            print(f"      Результат: {result}")
            parsed_count += 1
        else:
            print(f"  ❌ {i:3d}. {line}")
            unparsed_lines.append(line)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Распознано: {parsed_count}/{len(macbook_lines)} ({parsed_count/len(macbook_lines)*100:.1f}%)")
    print(f"  ❌ Нераспознано: {len(unparsed_lines)}")
    
    if unparsed_lines:
        print(f"\n❌ НЕРАСПОЗНАННЫЕ СТРОКИ ({len(unparsed_lines)}):")
        for i, line in enumerate(unparsed_lines, 1):
            print(f"   {i:2d}. {line}")
        print(f"\n🔧 НУЖНО ДОБАВИТЬ ПАТТЕРНЫ ДЛЯ {len(unparsed_lines)} СТРОК")
        print("Проанализируйте нераспознанные строки и добавьте соответствующие regex паттерны в macbook_parser.py")
    else:
        print(f"\n🎉 ОТЛИЧНО! MacBook парсер работает на 100%!")

if __name__ == "__main__":
    test_macbook_parser()
