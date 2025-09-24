#!/bin/bash

# Скрипт для проверки и очистки дублирующих процессов бота
# Использование: ./check_bot_processes.sh

set -e

# Конфигурация
SERVER_HOST="147.45.143.18"
SERVER_USER="root"

echo "🔍 Проверяем процессы бота на сервере $SERVER_HOST..."

ssh $SERVER_USER@$SERVER_HOST << EOF
    echo "📊 Текущие процессы бота:"
    ps aux | grep -E "(python.*bot/main.py|screen.*price_parser_bot)" | grep -v grep || echo "Процессы не найдены"
    
    echo ""
    echo "📊 Количество процессов:"
    # Считаем только python процессы, не screen (ищем процессы, которые НЕ являются screen)
    PYTHON_COUNT=\$(ps aux | grep -E "python.*bot/main.py" | grep -v grep | grep -v "SCREEN" | wc -l)
    SCREEN_COUNT=\$(ps aux | grep -E "SCREEN.*price_parser_bot" | grep -v grep | wc -l)
    echo "Python процессов бота: \$PYTHON_COUNT"
    echo "Screen сессий: \$SCREEN_COUNT"
    
    if [ "\$PYTHON_COUNT" -gt 1 ]; then
        echo "⚠️ Обнаружено \$PYTHON_COUNT python процессов бота! Очищаем дублирующие..."
        
        # Получаем PID всех python процессов бота (исключаем SCREEN)
        PIDS=\$(ps aux | grep -E "python.*bot/main.py" | grep -v grep | grep -v "SCREEN" | awk '{print \$2}')
        
        # Оставляем только первый процесс, остальные убиваем
        FIRST_PID=\$(echo "\$PIDS" | head -1)
        OTHER_PIDS=\$(echo "\$PIDS" | tail -n +2)
        
        echo "Оставляем процесс \$FIRST_PID"
        
        for pid in \$OTHER_PIDS; do
            echo "Завершаем дублирующий процесс \$pid"
            kill -TERM \$pid 2>/dev/null || true
        done
        
        sleep 2
        
        # Принудительно убиваем оставшиеся дублирующие процессы
        for pid in \$OTHER_PIDS; do
            if kill -0 \$pid 2>/dev/null; then
                echo "Принудительно завершаем процесс \$pid"
                kill -9 \$pid 2>/dev/null || true
            fi
        done
        
        echo "✅ Дублирующие процессы очищены"
    elif [ "\$PYTHON_COUNT" -eq 1 ] && [ "\$SCREEN_COUNT" -eq 1 ]; then
        echo "✅ Количество процессов в норме (1 python + 1 screen)"
    elif [ "\$PYTHON_COUNT" -eq 0 ]; then
        echo "⚠️ Бот не запущен! Нужно перезапустить."
    else
        echo "✅ Количество процессов в норме"
    fi
    
    echo ""
    echo "📊 Финальное состояние:"
    ps aux | grep -E "(python.*bot/main.py|screen.*price_parser_bot)" | grep -v grep || echo "Процессы не найдены"
EOF

echo "🎉 Проверка завершена!"
