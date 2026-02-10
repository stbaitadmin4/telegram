import sqlite3
import os

# Шлях до бази даних
# Важливо: припускаємо, що цей скрипт запускається з кореневої папки проєкту
DB_PATH = os.path.join('database', 'project_db.sqlite')

def check_database():
    """Перевіряє наявність користувачів та прав адміністратора."""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ПОМИЛКА: Файл бази даних не знайдено за шляхом: {DB_PATH}")
        print("Будь ласка, переконайтеся, що ви запустили ./setup_project.sh")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. ПЕРЕВІРКА АДМІНІСТРАТОРІВ
        print("\n--- 1. ПЕРЕВІРКА АДМІНІСТРАТОРІВ (ТАБЛИЦЯ admins) ---")
        cursor.execute("SELECT telegram_id, role FROM admins")
        admins = cursor.fetchall()

        if admins:
            print("✅ Знайдено адміністраторів:")
            for admin_id, role in admins:
                # Ваш актуальний ID користувача: 169588658
                status = "<- ВАШ ID (АКТУАЛЬНИЙ)" if str(admin_id) == '169588658' else ""
                print(f"   - ID: {admin_id}, Роль: {role} {status}")
        else:
            print("❌ ПОМИЛКА: Таблиця admins порожня. Немає жодного адміністратора.")

        # 2. ПЕРЕВІРКА КОРИСТУВАЧІВ
        print("\n--- 2. ПЕРЕВІРКА ТЕСТОВИХ КОРИСТУВАЧІВ (ТАБЛИЦЯ users) ---")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count > 0:
            print(f"✅ Знайдено {user_count} користувачів у таблиці users.")
            # Виводимо перші 3 для прикладу
            cursor.execute("SELECT first_name, last_name, telegram_account FROM users LIMIT 3")
            sample_users = cursor.fetchall()
            print("   Приклади користувачів:")
            for first, last, tg_acc in sample_users:
                 print(f"   - {first} {last} ({tg_acc})")
        else:
            print("❌ ПОМИЛКА: Таблиця users порожня.")

    except sqlite3.Error as e:
        print(f"❌ Виникла помилка SQLite: {e}")
    except Exception as e:
        print(f"❌ Невідома помилка: {e}")
    finally:
        if conn:
            conn.close()
            print("\n--- З'єднання з БД закрито. ---")

if __name__ == '__main__':
    check_database()