#!/usr/bin/env python3
import sys
sys.path.append('.')

from parsers.ipad_parser import iPadParser

def test_ipad_parser():
    """Тестирует iPad парсер на всех iPad строках из exampleprices.txt"""
    
    # Читаем файл с примерами цен
    try:
        with open('bot/exampleprices.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл bot/exampleprices.txt не найден!")
        return
    
    # Разбиваем на строки
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Фильтруем только iPad строки
    ipad_lines = []
    for line in lines:
        line_lower = line.lower()
        # Должна содержать iPad и не быть AirPods, Dyson, Mac, Watch и т.д.
        if 'ipad' in line_lower and not any(keyword in line_lower for keyword in [
            'airpods', 'dyson', 'mac', 'watch', 'aw ', 'pixel', 'galaxy', 'pencil', 'airtag', 
            'adapter', 'magic', 'mouse', 'keyboard', 'google', 'samsung'
        ]):
            ipad_lines.append(line)
    
    print(f"📱 Найдено {len(ipad_lines)} iPad строк для тестирования:")
    for i, line in enumerate(ipad_lines, 1):
        print(f"  {i:3d}. {line}")
    
    print(f"\n🧪 Тестируем iPad парсер:")
    
    # Создаем парсер
    ipad_parser = iPadParser()
    
    # Тестируем каждую строку
    parsed_count = 0
    unparsed_lines = []
    
    for i, line in enumerate(ipad_lines, 1):
        result = ipad_parser._parse_single_line(line)
        if result:
            print(f"  ✅ {i:3d}. {line}")
            print(f"      Результат: {result}")
            parsed_count += 1
        else:
            print(f"  ❌ {i:3d}. {line}")
            unparsed_lines.append(line)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Распознано: {parsed_count}/{len(ipad_lines)} ({parsed_count/len(ipad_lines)*100:.1f}%)")
    print(f"  ❌ Нераспознано: {len(unparsed_lines)}")
    
    if unparsed_lines:
        print(f"\n❌ НЕРАСПОЗНАННЫЕ СТРОКИ ({len(unparsed_lines)}):")
        for i, line in enumerate(unparsed_lines, 1):
            print(f"   {i:2d}. {line}")
        print(f"\n🔧 НУЖНО ДОБАВИТЬ ПАТТЕРНЫ ДЛЯ {len(unparsed_lines)} СТРОК")
        print("Проанализируйте нераспознанные строки и добавьте соответствующие regex паттерны в ipad_parser.py")
    else:
        print(f"\n🎉 ОТЛИЧНО! iPad парсер работает на 100%!")

if __name__ == "__main__":
    test_ipad_parser()

