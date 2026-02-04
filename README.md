# Todo App с AdminLTE

Веб-приложение для управления задачами (TODO) с красивым интерфейсом на базе AdminLTE и REST API.

## 🚀 Функциональность

- ✅ Создание, чтение, обновление и удаление задач (CRUD)
- ✅ Красивый веб-интерфейс на базе AdminLTE v4
- ✅ REST API с полной документацией Swagger UI
- ✅ SQLite/PostgreSQL база данных
- ✅ Дашборд со статистикой задач
- ✅ Адаптивный дизайн

## 📋 Требования

- Python 3.8+
- pip

## 🛠 Установка

### Способ 1: Docker (Рекомендуется)

#### Требования
- Docker
- Docker Compose

#### Быстрый старт с Docker Compose

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd flask_adminlte_app
   ```

2. **Создайте `.env` файл:**
   ```bash
   cp .env.example .env
   ```

   Отредактируйте `.env` файл:
   ```env
   SECRET_KEY=your-super-secret-key-change-in-production
   ```

3. **Запустите приложение с Docker Compose:**
   ```bash
   docker-compose up -d
   ```

   Приложение будет доступно по адресу: http://localhost:5000/dashboard

#### Команды Docker Compose

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка после изменений
docker-compose up -d --build

# Выполнение команд в контейнере
docker-compose exec todo-app flask db upgrade
docker-compose exec todo-app flask db migrate -m "Your migration message"
```

### Способ 2: Локальная установка

#### Требования
- Python 3.8+
- pip

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd flask_adminlte_app
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   # Linux/Mac
   python3 -m venv env-lin
   source env-lin/bin/activate

   # Windows
   python -m venv env-win
   source env-win/Scripts/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**

   Создайте файл `.env` на основе `env.sapmle`:
   ```bash
   cp env.sapmle .env
   ```

   Отредактируйте `.env` файл:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here

   # Для SQLite (по умолчанию):
   DATABASE_URL=sqlite:///todo.db

   # Для PostgreSQL:
   # DATABASE_URL=postgresql://username:password@localhost/todo_db
   ```

5. **Запустите приложение:**
   ```bash
   python app.py
   или
   flask run --host=0.0.0.0 --port=5000
   ```

  ## 📖 Использование

### Веб-интерфейс

- **Главная страница**: http://localhost:5000/dashboard
- **Дашборд**: Просмотр статистики и списка всех задач
- **Создание задачи**: `/todo/new` - форма для добавления новой задачи
- **Редактирование**: `/todo/<id>/edit` - редактирование существующей задачи
- **Удаление**: `/todo/<id>/delete` - удаление задачи
- **Переключение статуса**: `/todo/<id>/toggle` - отметка задачи как выполненной/невыполненной

### REST API

API доступно по адресу: http://localhost:5000/api/todos/

#### Эндпоинты:

- `GET /api/todos/` - Получить все задачи
- `POST /api/todos/` - Создать новую задачу
- `GET /api/todos/<id>/` - Получить задачу по ID
- `PUT /api/todos/<id>/` - Обновить задачу
- `DELETE /api/todos/<id>/` - Удалить задачу

#### Примеры использования API:

**Создание задачи:**
```bash
curl -X POST http://localhost:5000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Моя задача", "description": "Описание задачи", "completed": false}'
```

**Получение всех задач:**
```bash
curl http://localhost:5000/api/todos/
```

### Документация API

Полная интерактивная документация API доступна через Swagger UI:
- **Swagger UI**: http://localhost:5000/api/docs

## 🗄 Модель данных

### Todo
- `id` (Integer): Уникальный идентификатор
- `title` (String, required): Заголовок задачи
- `description` (String, optional): Описание задачи
- `completed` (Boolean): Статус выполнения
- `created_at` (DateTime): Дата создания
- `updated_at` (DateTime): Дата последнего обновления
- `due_date` (DateTime, optional): Дата выполнения задачи

## 🔄 Миграция базы данных

При изменении модели данных (добавлении полей, изменении типов) необходимо выполнить миграцию базы данных.

### Способ 1: Автоматическая миграция (рекомендуется)

1. **Установите Flask-Migrate:**
   ```bash
   pip install Flask-Migrate
   ```

2. **Инициализируйте миграции:**
   ```bash
   flask db init
   ```

3. **Создайте миграцию:**
   ```bash
   flask db migrate -m "Add due_date field to Todo model"
   ```

4. **Примените миграцию:**
   ```bash
   flask db upgrade
   ```

**Примечание:** Убедитесь, что переменная окружения `FLASK_APP` установлена:
```bash
export FLASK_APP=app.py  # Linux/Mac
# или
set FLASK_APP=app.py     # Windows
```

### Способ 2: Ручная миграция для SQLite

Если Flask-Migrate не используется, можно добавить столбцы вручную:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('instance/todo.db')
cursor = conn.cursor()
cursor.execute('ALTER TABLE todo ADD COLUMN due_date TIMESTAMP')
conn.commit()
conn.close()
print('Миграция завершена')
"
```

## 🏗 Архитектура проекта

```
flask_adminlte_app/
├── app.py              # Основное приложение Flask
├── requirements.txt    # Зависимости Python
├── .env               # Переменные окружения
├── static/            # Статические файлы
│   ├── css/
│   ├── js/
│   └── assets/
├── templates/         # HTML шаблоны
│   ├── base.html      # Базовый шаблон
│   ├── index.html     # Главная страница
│   └── todo_form.html # Форма задачи
└── README.md          # Эта документация
```

## 🛡 Безопасность

- CSRF защита включена
- Валидация входных данных
- Защита от SQL-инъекций через SQLAlchemy ORM

## 📱 Адаптивность

Приложение полностью адаптивно и корректно работает на:
- 📱 Мобильных устройствах
- 📺 Планшетах
- 💻 Настольных компьютерах

## 🔧 Настройка

### Смена базы данных

#### SQLite (по умолчанию)
SQLite используется по умолчанию и не требует дополнительной настройки.

#### PostgreSQL с Docker
Для использования PostgreSQL раскомментируйте секцию `postgres` в `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: todo_db
    POSTGRES_USER: todo_user
    POSTGRES_PASSWORD: todo_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  restart: unless-stopped
  networks:
    - todo-network
```

И добавьте в volumes:
```yaml
volumes:
  postgres_data:
```

Затем обновите переменную `DATABASE_URL` в `.env`:
```env
DATABASE_URL=postgresql://todo_user:todo_password@postgres:5432/todo_db
```

#### PostgreSQL локально
1. Установите PostgreSQL
2. Создайте базу данных: `createdb todo_db`
3. Обновите `.env` файл:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/todo_db
   ```
4. Перезапустите приложение

### Режимы работы

- **Development**: `FLASK_ENV=development` (с отладкой)
- **Production**: `FLASK_ENV=production` (без отладки)

### Docker продвинутые настройки

#### Кастомные переменные окружения

Создайте файл `.env` для настройки:

```env
# Flask настройки
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-in-production

# База данных
DATABASE_URL=sqlite:///instance/todo.db

# Дополнительные настройки
BABEL_DEFAULT_LOCALE=ru
BABEL_SUPPORTED_LOCALES=ru,en
```

#### Масштабирование

Для запуска нескольких экземпляров приложения:

```yaml
version: '3.8'

services:
  todo-app:
    build: .
    ports:
      - "5000-5002:5000"  # Диапазон портов
    deploy:
      replicas: 3
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://todo_user:todo_password@postgres:5432/todo_db
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - todo-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - todo-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - todo-app
    restart: unless-stopped
    networks:
      - todo-network

networks:
  todo-network:
    driver: bridge

volumes:
  postgres_data:
```

#### Nginx конфигурация (nginx.conf)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream todo_app {
        server todo-app:5000;
        server todo-app:5001;
        server todo-app:5002;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://todo_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/docs {
            proxy_pass http://todo_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Локализация (i18n)

Приложение поддерживает интернационализацию и поставляется с русским и английским языками по умолчанию.

#### Добавление нового языка (например, немецкого)

1. **Установите инструмент локализации:**
   ```bash
   pip install Babel
   ```

2. **Извлеките сообщения для перевода:**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

3. **Создайте каталог для нового языка:**
   ```bash
   pybabel init -i messages.pot -d translations -l de
   ```

4. **Отредактируйте файл перевода:**
   Откройте `translations/de/LC_MESSAGES/messages.po` и добавьте переводы для каждого msgid:
   ```po
   msgid "Home"
   msgstr "Startseite"

   msgid "Dashboard"
   msgstr "Dashboard"

   msgid "Language"
   msgstr "Sprache"

   msgid "Theme"
   msgstr "Thema"

   msgid "Dark"
   msgstr "Dunkel"

   msgid "Light"
   msgstr "Hell"

   msgid "Pagination"
   msgstr "Paginierung"

   msgid "per page"
   msgstr "pro Seite"

   msgid "Todo App"
   msgstr "Todo-App"

   msgid "Todos"
   msgstr "Aufgaben"

   msgid "All Todos"
   msgstr "Alle Aufgaben"

   msgid "Add Todo"
   msgstr "Aufgabe hinzufügen"

   msgid "API Docs"
   msgstr "API-Dokumentation"
   ```

5. **Скомпилируйте переводы:**
   ```bash
   pybabel compile -d translations
   ```

6. **Добавьте новый язык в конфигурацию приложения:**
   В файле `app.py` обновите настройки Babel:
   ```python
   app.config['BABEL_SUPPORTED_LOCALES'] = ['ru', 'en', 'de']  # Добавьте 'de'
   ```

7. **Добавьте опцию языка в шаблоне:**
   В файле `templates/base.html` добавьте ссылку на немецкий язык:
   ```html
   <li><a href="{{ url_for('set_language', lang='de') }}" class="dropdown-item{% if session.get('language', 'ru') == 'de' %} active{% endif %}"><i class="bi bi-check-circle-fill me-2{% if session.get('language', 'ru') != 'de' %} d-none{% endif %}"></i>Deutsch</a></li>
   ```

8. **Перезапустите приложение:**
   ```bash
   python app.py
   ```

Теперь немецкий язык будет доступен в меню "Options" -> "Language".

## 🐛 Решение проблем

### Ошибка подключения к базе данных
- Проверьте корректность `DATABASE_URL` в `.env`
- Убедитесь, что PostgreSQL сервер запущен (если используется PostgreSQL)

### Статические файлы не загружаются
- Проверьте, что файлы AdminLTE скопированы в папку `static/`
- Убедитесь в корректности путей в шаблонах

### API возвращает 404
- Проверьте, что приложение запущено
- Убедитесь, что используете правильные URL эндпоинтов

## 🤝 Вклад в проект

1. Форкните проект
2. Создайте ветку для вашей фичи: `git checkout -b feature/amazing-feature`
3. Зафиксируйте изменения: `git commit -m 'Add amazing feature'`
4. Отправьте изменения: `git push origin feature/amazing-feature`
5. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле LICENSE.

## 🙏 Благодарности

- [AdminLTE](https://adminlte.io/) - Отличный бесплатный шаблон админ-панели
- [Documentation](https://adminlte.io/docs/3.2/components/miscellaneous.html) - Документация по версии 3.1
- [Flask](https://flask.palletsprojects.com/) - Легковесный веб-фреймворк
- [Flask-RESTX](https://flask-restx.readthedocs.io/) - Расширение для создания REST API
- [SQLAlchemy](https://sqlalchemy.org/) - ORM для работы с базами данных

## 🌐 Компиляция файлов перевода

Для корректной работы локализации необходимо скомпилировать файлы перевода из формата .po в формат .mo:

### Установка Babel (если не установлен)

```bash
pip install Babel
```

### Компиляция переводов

```bash
# Компиляция всех файлов перевода
pybabel compile -d translations -D messages

# Альтернативно, можно использовать команду с указанием конкретного каталога
pybabel compile -d translations
```

### Обновление файлов перевода (если были изменения в шаблонах)

Если вы добавили новые строки для перевода в шаблонах, выполните следующие шаги:

1. **Извлечение сообщений:**
   ```bash
   pybabel extract -F babel.cfg -o translations/messages.pot .
   ```

2. **Обновление существующих файлов перевода:**
   ```bash
   pybabel update -i translations/messages.pot -d translations
   ```

3. **Редактирование файлов перевода:**
   Откройте файлы `translations/ru/LC_MESSAGES/messages.po` и `translations/en/LC_MESSAGES/messages.po` и добавьте недостающие переводы.

4. **Компиляция файлов перевода:**
   ```bash
   pybabel compile -d translations -D messages
   ```

После компиляции файлов перевода изменения в локализации станут доступны в приложении. Убедитесь, что перезапустили сервер приложений после компиляции файлов перевода.