"""iTradeBot — точка входа."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_ID, SITE_URL
from database import init_db
from handlers import start, sell, buy, games, my_orders, about, support, review, admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("itradebot")


async def main():
    log.info("🚀 Запускаю iTradeBot...")
    log.info(f"ADMIN_ID = {ADMIN_ID}")
    log.info(f"SITE_URL = {SITE_URL}")

    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(sell.router)
    dp.include_router(buy.router)
    dp.include_router(games.router)
    dp.include_router(my_orders.router)
    dp.include_router(about.router)
    dp.include_router(support.router)
    dp.include_router(review.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")


