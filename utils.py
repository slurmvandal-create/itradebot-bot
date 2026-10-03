"""Утилиты: разбор payload, форматирование."""
from datetime import datetime


def parse_payload(payload: str) -> dict:
    if not payload:
        return {"type": "empty", "raw": ""}
    parts = payload.split("_", 3)
    kind = parts[0]

    if kind == "sell":
        result = {"type": "sell"}
        if len(parts) >= 2: result["device"] = parts[1]
        if len(parts) >= 3: result["model"] = parts[2].replace("-", " ")
        if len(parts) >= 4: result["condition"] = parts[3]
        return result

    if kind == "buy" and len(parts) >= 2:
        return {"type": "buy", "item_id": parts[1]}

    return {"type": kind, "raw": payload}


CONDITIONS_RU = {
    "ideal": "Идеальное",
    "good": "Хорошее",
    "worn": "Заметные следы",
}

DEVICES_RU = {
    "iphone": "iPhone",
    "ipad": "iPad",
    "macbook": "MacBook",
    "ps": "PlayStation",
}

STATUS_RU = {
    "new": "🆕 Новая",
    "in_progress": "🔄 В работе",
    "done": "✅ Завершена",
    "cancelled": "❌ Отменена",
}


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso