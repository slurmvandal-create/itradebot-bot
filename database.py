"""SQLite-база: заявки и отзывы."""
import sqlite3
from datetime import datetime
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            device TEXT,
            model TEXT,
            condition TEXT,
            price INTEGER,
            contact TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            text TEXT,
            photo_id TEXT,
            rating INTEGER,
            published INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_order(user_id, username, full_name, device, model, condition, price, contact):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (user_id, username, full_name, device, model, condition, price, contact, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, full_name, device, model, condition, price, contact, datetime.now().isoformat()))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_user_orders(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, device, model, condition, price, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_orders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, user_id, username, full_name, device, model, condition, price, contact, status, created_at FROM orders ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def update_order_status(order_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def add_review(user_id, username, full_name, text, photo_id, rating):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO reviews (user_id, username, full_name, text, photo_id, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, full_name, text, photo_id, rating, datetime.now().isoformat()))
    review_id = c.lastrowid
    conn.commit()
    conn.close()
    return review_id


def get_all_reviews(only_unpublished=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if only_unpublished:
        c.execute("SELECT id, user_id, full_name, text, photo_id, rating, published, created_at FROM reviews WHERE published = 0 ORDER BY id DESC")
    else:
        c.execute("SELECT id, user_id, full_name, text, photo_id, rating, published, created_at FROM reviews ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def publish_review(review_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE reviews SET published = 1 WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()


def get_published_reviews():
    """Для возможной выгрузки на сайт через API в будущем."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT full_name, text, photo_id, rating, created_at FROM reviews WHERE published = 1 ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_user_ids():
    """Для рассылки."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT user_id FROM orders UNION SELECT DISTINCT user_id FROM reviews")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]