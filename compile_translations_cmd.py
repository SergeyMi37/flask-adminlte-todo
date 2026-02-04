#!/usr/bin/env python
"""
Команда для компиляции файлов перевода Flask-Babel
"""

import subprocess
import sys
import os

def compile_translations():
    """Компиляция файлов перевода с помощью pybabel"""
    print("Компиляция файлов перевода с использованием pybabel...")
    
    try:
        # Выполняем команду компиляции
        result = subprocess.run([
            sys.executable, "-m", "babel.messages.frontend", "compile",
            "--directory", "translations",
            "--domain", "messages"
        ], capture_output=True, text=True, check=True)
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print("Компиляция файлов перевода успешно завершена!")
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при компиляции переводов: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        
        # Попробуем альтернативный способ
        try:
            import subprocess
            result = subprocess.run([
                "pybabel", "compile",
                "--directory", "translations",
                "--domain", "messages"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Компиляция успешно завершена с помощью pybabel")
                print(result.stdout)
            else:
                print("Ошибка pybabel:", result.stderr)
                
        except FileNotFoundError:
            print("pybabel не найден. Установите его с помощью 'pip install Babel'")
    
    except ImportError:
        print("Модуль babel.messages.frontend не найден. Установите Babel: pip install Babel")

if __name__ == "__main__":
    compile_translations()