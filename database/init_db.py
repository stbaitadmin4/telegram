import sqlite3
import datetime
import os

# --- КОНФІГУРАЦІЯ БАЗИ ДАНИХ ---
DB_NAME = 'project_db.sqlite'
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# !!! ВАШ ОСОБИСТИЙ TELEGRAM ID !!!
# Замініть це на ваш реальний ID користувача Telegram.
ADMIN_TELEGRAM_ID = 169588658  # <-- ПРИКЛАД: ВСТАВТЕ СВІЙ АКТУАЛЬНИЙ ID

def init_db():
    """Ініціалізує базу даних: видаляє стару, створює таблиці та заповнює тестовими даними."""
    
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    
    # Видаляємо стару БД для чистого старту
    if os.path.exists(db_path):
        print(f"🗑️ Видалення існуючої бази даних: {DB_NAME}")
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Створення таблиць
        print("🛠️ Створення таблиць зі schema.sql...")
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            cursor.executescript(sql_script)

        # 2. Додавання 10 тестових користувачів
        print("🧑‍💻 Додавання 10 тестових користувачів...")
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        test_users = [
            ('Олена', 'Мила', '1995-11-20', '+380634569045', '@mlch24', now),
            ('Олена', 'Коваль', '1995-10-20', '380674445566', '@olena_koval23231', now),
            ('Максим', 'Сидоренко', '1985-01-01', '380937778899', '@max_sydsfwf', now),
            ('Юлія', 'Шевченко', '2000-03-10', '380998887766', '@yulia_shev12313', now),
            ('Андрій', 'Гриценко', '1988-11-22', '380631234567', '@andriy_gsssff', now),
            ('Наталія', 'Мельник', '1993-07-07', '380969876543', '@nata_mfwf24', now),
            ('Віктор', 'Палій', '1975-02-28', '380971112233', '@viktor_p4234s', now),
            ('Ірина', 'Лисенко', '1998-12-05', '380954443322', '@ira_lys34sfg1', now),
            ('Олег', 'Кравченко', '1980-08-18', '380685554433', '@oleg_krav32525rf', now),
            ('Тетяна', 'Коваленко', '1992-04-03', '380667778899', '@tanya_kovfsgsg4', now),
        ]
        
        cursor.executemany("""
            INSERT INTO users (first_name, last_name, date_of_birth, phone_number, telegram_account, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_users)

        # 3. Додавання User Admin'а
        print(f"🔑 Додавання адміністратора з Telegram ID: {ADMIN_TELEGRAM_ID}")
        cursor.execute("""
            INSERT OR IGNORE INTO admins (telegram_id, role) VALUES (?, ?)
        """, (ADMIN_TELEGRAM_ID, 'user_manager'))

        conn.commit()
        print("✅ База даних успішно ініціалізована та заповнена тестовими даними.")

    except sqlite3.Error as e:
        print(f"❌ Виникла помилка SQLite: {e}")
    except IOError as e:
        print(f"❌ Помилка читання файлу схеми: {SCHEMA_PATH}. Переконайтесь, що він існує.")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()