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
        log.error("❌ DATABASE_URL не найден!")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            avatar_file_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            full_name TEXT,
            device TEXT,
            model TEXT,
            condition TEXT,
            price INTEGER,
            contact TEXT,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            full_name TEXT,
            text TEXT,
            photo_id TEXT,
            rating INTEGER,
            is_published BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    log.info("✅ Таблицы успешно созданы или уже существуют!")


# ---------- ПОЛЬЗОВАТЕЛИ ----------

def add_user(telegram_id, username=None, full_name=None, avatar_file_id=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (telegram_id, username, full_name, avatar_file_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO UPDATE
        SET username = EXCLUDED.username,
            full_name = EXCLUDED.full_name,
            avatar_file_id = COALESCE(EXCLUDED.avatar_file_id, users.avatar_file_id)
    """, (telegram_id, username, full_name, avatar_file_id))
    conn.commit()
    cur.close()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT telegram_id, username, full_name, avatar_file_id, created_at "
        "FROM users WHERE telegram_id = %s", (telegram_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_all_user_ids():
    """Возвращает список telegram_id всех пользователей."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id FROM users")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ---------- ЗАКАЗЫ ----------

def add_order(user_id, username=None, full_name=None, device=None,
              model=None, condition=None, price=None, contact=None):
    """Создает заявку, возвращает её id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, username, full_name, device, model, condition, price, contact)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (user_id, username, full_name, device, model, condition, price, contact))
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return order_id


def get_user_orders(user_id):
    """Заявки пользователя: (id, device, model, condition, price, status, created_at)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, device, model, condition, price, status, created_at
        FROM orders WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_all_orders():
    """Все заявки: (id, user_id, username, full_name, device, model, condition, price, contact, status, created_at)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, username, full_name, device, model, condition, price, contact, status, created_at
        FROM orders
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    cur.close()
    conn.close()


# ---------- ОТЗЫВЫ ----------

def add_review(user_id, username=None, full_name=None, text=None, photo_id=None, rating=None):
    """Создает отзыв, возвращает его id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews (user_id, username, full_name, text, photo_id, rating)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (user_id, username, full_name, text, photo_id, rating))
    review_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return review_id


def get_all_reviews():
    """Все отзывы: (id, user_id, full_name, text, photo_id, rating, is_published, created_at)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, full_name, text, photo_id, rating, is_published, created_at
        FROM reviews
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def publish_review(review_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE reviews SET is_published = TRUE WHERE id = %s", (review_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_published_reviews():
    """Опубликованные отзывы (для сайта)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, full_name, text, photo_id, rating, created_at
        FROM reviews
        WHERE is_published = TRUE
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
def get_all_users():
    """Все пользователи: (telegram_id, username, full_name, created_at)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, username, full_name, created_at FROM users ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_pending_reviews():
    """Отзывы, ожидающие модерации."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, full_name, text, photo_id, rating, created_at
        FROM reviews WHERE is_published = FALSE
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def delete_review(review_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    cur.close()
    conn.close()


def delete_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_order_by_id(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, username, full_name, device, model, condition, price, contact, status, created_at
        FROM orders WHERE id = %s
    """, (order_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_stats():
    """Простая статистика: (кол-во юзеров, кол-во заявок, кол-во отзывов)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders")
    orders_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reviews")
    reviews_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return users_count, orders_count, reviews_count


def list_user_orders(user_id):
    """Псевдоним для get_user_orders."""
    return get_user_orders(user_id)
