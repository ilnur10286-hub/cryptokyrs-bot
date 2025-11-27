import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGETS = {}
VALID_COINS = ["bitcoin", "ethereum", "aptos", "solana"]

def get_session():
    msk = datetime.now(timezone(timedelta(hours=3)))
    h = msk.hour
    if 2 <= h < 10: return "🌏 Азиатская"
    elif 10 <= h < 16: return "🇪🇺 Европейская"
    elif 16 <= h or h < 1: return "🇺🇸 Американская"
    else: return "🌙 Тихая зона"

# === ВСЕ ФУНКЦИИ (kurs, tsel, tseli, list_cmd, raspisanie, start) — как у тебя ===
# (вставь их сюда без изменений)

# === ЗАПУСК ===
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kurs", kurs))
    app.add_handler(CommandHandler("tsel", tsel))
    app.add_handler(CommandHandler("tseli", tseli))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("raspisanie", raspisanie))
    app.run_polling()
