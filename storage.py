import os
import base64
import aiohttp
from dotenv import load_dotenv

load_dotenv()

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")


async def upload_photo_to_storage(bot, file_id: str, folder: str = "reviews") -> str:
    """
    Скачивает фото из Telegram и загружает на ImgBB.
    Возвращает публичный URL для сайта.
    """
    # 1. Получаем информацию о файле
    file_info = await bot.get_file(file_id)

    # 2. Скачиваем фото в память
    file_bytes = await bot.download_file(file_info.file_path)

    # 3. Кодируем в base64 (обязательно для ImgBB)
    image_base64 = base64.b64encode(file_bytes.read()).decode("utf-8")

    # 4. Отправляем на ImgBB
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": image_base64,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            result = await response.json()

    if result.get("success"):
        return result["data"]["display_url"]
    else:
        raise Exception(f"Ошибка загрузки на ImgBB: {result}")
