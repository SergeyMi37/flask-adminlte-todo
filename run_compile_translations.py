#!/usr/bin/env python
"""
Скрипт для компиляции файлов перевода
"""

import os
import subprocess
import sys

def main():
    """Основная функция для компиляции переводов"""
    print("Запуск компиляции файлов перевода...")
    
    # Проверяем, что мы находимся в правильной директории
    if not os.path.exists("translations"):
        print("Ошибка: Каталог 'translations' не найден в текущей директории.")
        return
    
    # Команда для компиляции переводов
    cmd = [
        sys.executable, "-m", "babel.messages.frontend", "compile_catalog",
        "--directory", "translations",
        "--domain", "messages"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Компиляция успешно завершена!")
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")
        print(f"Код возврата: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        
        # Альтернативный способ через pybabel напрямую
        print("\nПопытка компиляции через pybabel...")
        try:
            # Убедимся, что pybabel установлен
            import babel
            print(f"Babel версия: {babel.__version__}")
            
            # Попробуем выполнить команду через os.system
            os.system('pybabel compile -d translations -D messages')
        except ImportError:
            print("PyBabel не установлен. Пожалуйста, установите его: pip install Babel")
    except FileNotFoundError:
        print("Python модуль babel.messages.frontend не найден")
        print("Попробуйте установить Babel: pip install Babel")

if __name__ == "__main__":
    main()