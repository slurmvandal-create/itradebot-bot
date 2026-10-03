from database import init_db, get_connection
from storage import upload_photo_to_storage, IMGBB_API_KEY

def test_db():
    try:
        init_db()
        conn = get_connection()
        print("✅ PostgreSQL подключение OK")
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")

def test_imgbb():
    if not IMGBB_API_KEY:
        print("❌ IMGBB_API_KEY не найден в .env")
        return
    print(f"✅ IMGBB_API_KEY найден (начинается с: {IMGBB_API_KEY[:8]}...)")

if __name__ == "__main__":
    test_db()
    test_imgbb()
