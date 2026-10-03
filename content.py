"""Тексты и данные каталога."""

ABOUT_TEXT = (
    "ℹ️ <b>О нас</b>\n\n"
    "iTradeBot — сервис выкупа и продажи техники в Екатеринбурге.\n\n"
    "📍 <b>Адрес:</b> Екатеринбург, ул. Малышева, 51 (БЦ «Высоцкий»)\n"
    "🕐 <b>Часы работы:</b> Пн–Сб, 10:00–20:00\n"
    "📞 <b>Телефон:</b> +7 (999) 123-45-67\n"
    "✉️ <b>Email:</b> hello@itradebot.ru\n\n"
    "🚚 Бесплатная доставка по Екатеринбургу\n"
    "📦 Отправка по России (СДЭК, Почта)"
)

# Каталог (мок-данные, потом заменить на API/БД)
CATALOG = {
    "iphone": [
        {"name": "iPhone 15 Pro", "meta": "256 GB · Natural Titanium", "price": 89990},
        {"name": "iPhone 14", "meta": "128 GB · Blue", "price": 54990},
    ],
    "ipad": [
        {"name": 'iPad Pro 11" M4', "meta": "256 GB · Space Gray", "price": 84990},
        {"name": "iPad Air", "meta": "64 GB · Starlight", "price": 42990},
    ],
    "macbook": [
        {"name": "MacBook Air M2", "meta": '13" · 8/256 GB', "price": 94990},
        {"name": 'MacBook Pro 14" M3', "meta": "18/512 GB", "price": 169990},
    ],
    "ps": [
        {"name": "PlayStation 5 Slim", "meta": "1 TB · с дисководом", "price": 52990},
        {"name": "PlayStation 5", "meta": "825 GB · Digital", "price": 46990},
    ],
}

GAMES_NEW = [
    {"name": "FC 26", "meta": "PS5 · диск", "price": 4990},
    {"name": "Assassin's Creed Shadows", "meta": "PS5 · диск", "price": 5990},
]

GAMES_HITS = [
    {"name": "God of War Ragnarök", "meta": "PS5 · диск", "price": 3490},
    {"name": "Spider-Man 2", "meta": "PS5 · диск", "price": 3990},
    {"name": "The Last of Us Part II Remastered", "meta": "PS5 · диск", "price": 4290},
]