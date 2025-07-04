# Quotes Bot

Telegram-бот для отправки случайных цитат пользователям из базы данных. 
Позволяет получать, добавлять и оценивать цитаты, а также формировать PDF-файл с лучшими цитатами.

---

## Возможности

- Получение случайной цитаты по кнопке или по расписанию
- Оценка цитат (лайк/дизлайк)
- Добавление собственных цитат через загрузку markdown-файла
- Генерация PDF-файла с лучшими цитатами (набрали больше всего лайков)
- Гибкая настройка частоты получения цитат (от раз в минуту до 4 раз в день)

---

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/yourusername/quotes_bot.git
   cd quotes_bot
   ```
2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   # или
   pip install uv  # если используете uv
   uv pip install -r requirements.txt
   ```
   Или используйте зависимости из `pyproject.toml`:
   ```bash
   pip install -r pyproject.toml
   ```
4. **Создайте файл .env и добавьте токен Telegram-бота:**
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   ```
5. **Инициализируйте базу данных:**
   ```bash
   python db/db_init.py
   ```
6. **Запустите бота:**
   ```bash
   python main.py
   ```

---

## Использование

- После запуска бота используйте команду `/start` в Telegram.
- Доступные команды и кнопки:
  - 📚 Get a Random Quote — получить случайную цитату
  - Add quotes — добавить свои цитаты (загрузите .md-файл)
  - Best_quotes — получить PDF с лучшими цитатами
  - /settings — настроить частоту получения цитат
- Оценка цитат: после получения цитаты можно поставить лайк или дизлайк.

### Формат файла для импорта цитат

- **Markdown (.md):**
  - Структура:
    ```md
    ---
    Название: Название книги
    Автор: Имя автора
    ---
    Цитата 1
    ---
    Цитата 2
    ---
    ...
    ```
- **CSV:**
  - Можно преобразовать CSV в markdown с помощью скрипта `app/make_quotes_from_csv.py`.

---

## Структура проекта

```
quotes_bot/
├── app/                # Основная логика бота
│   ├── bot.py          # Логика Telegram-бота
│   ├── get_random_line.py  # Получение случайной цитаты
│   ├── make_pdf.py     # Генерация PDF с лучшими цитатами
│   ├── quotes_from_md.py   # Импорт цитат из markdown
│   ├── make_quotes_from_csv.py # Преобразование CSV в markdown
│   ├── book.py         # Класс Book_quotes
│   └── DejaVuSans.ttf  # Шрифт для PDF
├── db/                 # Работа с базой данных
│   ├── db_init.py      # Инициализация базы
│   ├── db_fill_in.py   # Импорт цитат
│   ├── db_modify.py    # Оценка цитат
├── main.py             # Точка входа
├── pyproject.toml      # Зависимости
├── uv.lock             # Лок-файл зависимостей
├── .env                # Переменные окружения (не входит в git)
├── .gitignore          # Исключения для git
├── safety.md           # Рекомендации по безопасности
└── README.md           # Описание проекта
```

---

## Безопасность

- Не храните токен бота в открытом виде — используйте .env
- Следите за обновлением зависимостей
- Не загружайте вредоносные файлы (бот проверяет расширение, но не содержимое)
- Подробнее — см. файл `safety.md`

---

## Вклад

Pull requests приветствуются! Открывайте issues для багов и предложений.

---

## Лицензия

MIT License

---

## Контакты

Автор: Alexandr Fedosov
E-mail: alexfedosov1985@gmail.com
Telegram: @aufed

---

## Благодарности

- [python-telegram-bot](https://python-telegram-bot.org/)
- [reportlab](https://www.reportlab.com/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
