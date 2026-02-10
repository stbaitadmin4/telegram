-- Таблиця для користувачів
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,         -- Зберігаємо як текст 'YYYY-MM-DD'
    phone_number TEXT UNIQUE,   -- Має бути унікальним
    telegram_account TEXT UNIQUE, -- Має бути унікальним (наприклад, @username)
    registration_date TEXT NOT NULL -- Дата реєстрації 'YYYY-MM-DD HH:MM:SS'
);

-- Таблиця для User Admin'а (реалізація політик доступу)
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL, -- ID користувача Telegram, який має право керувати базою
    role TEXT NOT NULL DEFAULT 'user_manager'
);