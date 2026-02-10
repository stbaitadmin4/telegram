import logging
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram import filters 
import sqlite3
import os
import asyncio
from datetime import datetime

# --- КОНФІГУРАЦІЯ ---
API_ID = 38630390              
API_HASH = "781ed0856bd6bd88bef541cf197fc35e"  

SESSION_NAME = "user_management_session"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'project_db.sqlite')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- ФУНКЦІЇ ВЗАЄМОДІЇ З БД (ОНОВЛЕНО: Тепер повертає telegram_id) ---

def is_admin(user_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (user_id,))
        return cursor.fetchone() is not None
    finally:
        if conn:
            conn.close()

def get_all_users_for_broadcast():
    """Витягує список лише Telegram ID для розсилки."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # ПРИПУЩЕННЯ: Ви додали стовпець telegram_id в таблицю users
        # Якщо ні, ця функція поверне помилку. Потрібно використовувати telegram_account
        cursor.execute("SELECT telegram_account FROM users") 
        # Якщо ви зберігаєте чистий ID користувача: cursor.execute("SELECT telegram_id FROM users")
        return [row[0] for row in cursor.fetchall()]
    finally:
        if conn:
            conn.close()

# --- (Інші функції БД без змін) ---
def get_all_users():
    # ... (функція залишається для команди /get_users) ...
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, telegram_account FROM users")
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()

def add_new_user(first_name, last_name, dob, phone, telegram_acc):
    # ... (функція залишається) ...
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO users (first_name, last_name, date_of_birth, phone_number, telegram_account, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, dob, phone, telegram_acc, registration_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    except Exception as e:
        logger.error(f"Помилка додавання користувача: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- ОСНОВНИЙ ОБРОБНИК КОМАНД (ДОДАНО /broadcast) ---

async def command_handler(client, message):
    
    if not message.text or not message.from_user:
        return

    sender_id = message.from_user.id
    
    # 🛡️ ПЕРЕВІРКА АДМІНІСТРАТОРА
    if not is_admin(sender_id):
        if message.text.startswith(("/add_user", "/get_users", "/broadcast")):
            await message.reply_text("⛔️ Доступ заборонено. Тільки адміністратори можуть використовувати цю команду.")
        return 

    # 1. Обробка команди /get_users (без змін)
    if message.text.lower() == "/get_users":
        # ... (логіка) ...
        users_data = get_all_users()
        if users_data:
            response = "📊 **Список зареєстрованих користувачів:**\n\n"
            for first, last, tg_acc in users_data:
                response += f"- **{first} {last}** ({tg_acc})\n"
        else:
            response = "База даних користувачів порожня."
        await message.reply_text(response, parse_mode='Markdown')

    # 2. Обробка команди /add_user (без змін)
    elif message.text.startswith("/add_user"):
        # ... (логіка) ...
        parts = message.text.split()
        if len(parts) != 6:
            await message.reply_text("Помилка: Неправильний формат.\nВикористовуйте: `/add_user Ім'я Прізвище ДДДД-ММ-ДД Телефон @ТелеграмАкаунт`", parse_mode='Markdown')
            return
        try:
            _, first_name, last_name, dob, phone, telegram_acc = parts
        except ValueError:
            await message.reply_text("Помилка: Не вдалося розпарсити всі параметри. Перевірте формат.")
            return

        if add_new_user(first_name, last_name, dob, phone, telegram_acc):
            await message.reply_text(f"✅ Користувач **{first_name} {last_name}** успішно доданий до бази даних.", parse_mode='Markdown')
        else:
            await message.reply_text("❌ Помилка при додаванні користувача. Можливо, телефон або Telegram-акаунт вже існує.")
            
    # 3. Обробка команди /broadcast (НОВИЙ ФУНКЦІОНАЛ)
    elif message.text.startswith("/broadcast"):
        
        message_parts = message.text.split(maxsplit=1)
        if len(message_parts) < 2:
            await message.reply_text("Помилка: Вкажіть повідомлення для розсилки.\nВикористовуйте: `/broadcast Привіт, це тестове повідомлення.`", parse_mode='Markdown')
            return

        broadcast_text = message_parts[1].strip()
        
        # Отримуємо список отримувачів (Telegram username/ID)
        recipients = get_all_users_for_broadcast()
        
        if not recipients:
            await message.reply_text("❌ Немає користувачів для розсилки в базі даних.", parse_mode='Markdown')
            return
        
        success_count = 0
        
        await message.reply_text(f"🚀 Починаю розсилку {len(recipients)} користувачам...")

        for recipient in recipients:
            try:
                # recipient може бути Telegram ID (як число) або username (як @username)
                await client.send_message(recipient, broadcast_text)
                success_count += 1
                await asyncio.sleep(0.1) # Затримка для уникнення FloodWait
            except Exception as e:
                # Тут можуть бути помилки, якщо користувач заблокував клієнта
                logger.warning(f"Помилка відправки повідомлення користувачу {recipient}: {e}")
        
        await message.reply_text(f"✅ Розсилку завершено!\nУспішно доставлено: **{success_count}** з {len(recipients)}.", parse_mode='Markdown')


# --- ЗАПУСК КЛІЄНТА ---

app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

async def main_async():
    await app.start()
    
    # Реєструємо обробник для всіх трьох команд
    app.add_handler(MessageHandler(command_handler, filters.command(["get_users", "add_user", "broadcast"])))
    
    logger.info("🤖 Telegram API Server запущено. Натисніть Ctrl+C для зупинки.")
    
    # Виводимо актуальний ID адміністратора для довідки
    try:
        me = await app.get_me()
        logger.info(f"🔑 Актуальний ID клієнта: {me.id}")
    except:
        pass
        
    await asyncio.Event().wait()


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Сервер зупинено.")
    except Exception as e:
        logger.error(f"Виникла загальна помилка: {e}")

if __name__ == '__main__':
    main()