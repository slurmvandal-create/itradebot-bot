"""Работа с базой данных PostgreSQL."""
import os
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_connection():
    """Возвращает соединение с БД."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    """Создает таблицы, если их нет."""
    if not DATABASE_URL:
        log.error("❌ DATABASE_URL не найден! Проверьте переменные окружения.")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            avatar_file_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
    log.info("✅ Таблицы успешно созданы или уже существуют!")


# ---------- ПОЛЬЗОВАТЕЛИ ----------

def add_user(telegram_id: int, username: str = None, first_name: str = None):
    """Создаёт или обновляет пользователя."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id) DO UPDATE
        SET username = EXCLUDED.username,
            first_name = EXCLUDED.first_name
    """, (telegram_id, username, first_name))
    conn.commit()
    cur.close()
    conn.close()


def get_user(telegram_id: int):
    """Возвращает данные пользователя или None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, username, first_name FROM users WHERE telegram_id = %s", (telegram_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


# ---------- ЗАКАЗЫ ----------

def add_order(user_id: int, category: str, description: str, telegram_file_id: str = None):
    """Добавляет заказ, возвращает его id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, category, description, telegram_file_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, category, description, telegram_file_id))
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"📦 Добавлен заказ #{order_id} от пользователя {user_id}")
    return order_id


def get_user_orders(user_id: int):
    """Возвращает список заказов конкретного пользователя."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, category, description, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_all_orders():
    """Возвращает все заказы (для админа)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, category, description, status, created_at
        FROM orders
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_order_by_id(order_id: int):
    """Возвращает один заказ по id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, category, description, telegram_file_id, status, created_at
        FROM orders
        WHERE id = %s
    """, (order_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def update_order_status(order_id: int, status: str):
    """Обновляет статус заказа."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"🔄 Заказ #{order_id} → статус '{status}'")


# ---------- ОТЗЫВЫ ----------

def add_review(user_id: int, text: str, rating: int, telegram_file_id: str = None):
    """Добавляет отзыв, возвращает его id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews (user_id, text, rating, telegram_file_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, text, rating, telegram_file_id))
    review_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"⭐ Добавлен отзыв #{review_id} от пользователя {user_id} (оценка {rating})")
    return review_id


def get_reviews(published_only: bool = False):
    """
    Возвращает отзывы.
    Если published_only=True — только опубликованные (для сайта).
    Если False — все (для админ-панели).
    """
    conn = get_connection()
    cur = conn.cursor()
    if published_only:
        cur.execute("""
            SELECT id, user_id, text, rating, telegram_file_id, created_at
            FROM reviews
            WHERE is_published = TRUE
            ORDER BY created_at DESC
        """)
    else:
        cur.execute("""
            SELECT id, user_id, text, rating, telegram_file_id, is_published, created_at
            FROM reviews
            ORDER BY created_at DESC
        """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def publish_review(review_id: int):
    """Публикует отзыв (is_published = TRUE)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE reviews SET is_published = TRUE WHERE id = %s", (review_id,))
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"📢 Отзыв #{review_id} опубликован")


def delete_review(review_id: int):
    """Удаляет отзыв."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"🗑 Отзыв #{review_id} удалён")
