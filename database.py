import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ВАЖНО: заменяем префикс для psycopg2
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    """Возвращает соединение с БД."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    """Создает таблицы, если их нет."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            avatar_file_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица заказов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(telegram_id),
            category TEXT,
            description TEXT,
            telegram_file_id TEXT,
            status TEXT DEFAULT 'В обработке',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица отзывов (ДОБАВЬТЕ ЭТОТ БЛОК)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(telegram_id),
            text TEXT,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            telegram_file_id TEXT,
            is_published BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблицы успешно созданы или уже существуют!")
