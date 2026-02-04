#!/usr/bin/env python
"""
Скрипт для компиляции файлов перевода Flask-Babel
"""

import os
from babel.messages.frontend import compile_catalog

def compile_translations():
    """Компиляция файлов перевода"""
    print("Компиляция файлов перевода...")
    
    # Путь к каталогу с переводами
    translations_dir = os.path.join(os.getcwd(), 'translations')
    
    if not os.path.exists(translations_dir):
        print(f"Каталог {translations_dir} не найден!")
        return
    
    # Проходим по всем подкаталогам в поисках .po файлов
    for root, dirs, files in os.walk(translations_dir):
        for file in files:
            if file.endswith('.po'):
                po_file = os.path.join(root, file)
                mo_file = os.path.join(root, file.replace('.po', '.mo'))
                
                print(f"Компиляция {po_file} -> {mo_file}")
                
                # Используем babel для компиляции
                compiler = compile_catalog()
                compiler.directory = root
                compiler.domain = 'messages'
                compiler.use_fuzzy = True
                compiler.finalize_options()
                compiler.run()
                
    print("Компиляция завершена!")

if __name__ == "__main__":
    compile_translations()