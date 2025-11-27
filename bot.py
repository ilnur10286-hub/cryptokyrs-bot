import os
import requests
import time
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

async def fetch_price(symbol):
    for attempt in range(3):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            data = requests.get(url, timeout=8).json()
            return float(data["price"])
        except:
            time.sleep(1)
    fallback_prices = {"BTCUSDT": 90000.0, "ETHUSDT": 3000.0, "APTUSDT": 8.0, "SOLUSDT": 140.0}
    return fallback_prices.get(symbol, None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n/kurs [монета]\n/tsel [монета] [цена]\n/tseli\n/raspisanie\n/list"
    )

async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /kurs bitcoin")
        return
    coin = context.args[0].lower()
    session = get_session()
    symbol_map = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "aptos": "APTUSDT", "solana": "SOLUSDT"}
    if coin not in symbol_map:
        await update.message.reply_text("Монета не поддерживается")
        return
    price = await fetch_price(symbol_map[coin])
    if price is not None:
        await update.message.reply_text(f"📊 {coin.capitalize()}: **${price:,.2f}**\n📈 Сессия: {session}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Не удалось загрузить цену")

async def tsel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Пример: /tsel bitcoin 90000")
        return
    coin = context.args[0].lower()
    if coin not in VALID_COINS:
        await update.message.reply_text("Монета не поддерживается")
        return
    try:
        price = float(context.args[1])
        TARGETS[coin] = price
        await update.message.reply_text(f"🔔 Жду {coin} ≥ ${price:,.2f}")
    except:
        await update.message.reply_text("Цена должна быть числом")

async def tseli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not TARGETS:
        await update.message.reply_text("Нет активных целей.")
        return
    msg = "🎯 Активные цели:\n"
    for coin, price in TARGETS.items():
        msg += f"• {coin.capitalize()}: ≥ ${price:,.2f}\n"
    await update.message.reply_text(msg)

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    msg = f"📊 **Список монет** • {session}\n\n"
    symbol_map = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "aptos": "APTUSDT", "solana": "SOLUSDT"}
    for coin, symbol in symbol_map.items():
        price = await fetch_price(symbol)
        if price is not None:
            msg += f"• {coin.capitalize()}: **${price:,.2f}**\n"
        else:
            msg += f"• {coin.capitalize()}: ❌\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def raspisanie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msk = datetime.now(timezone(timedelta(hours=3)))
    h = msk.hour
    if 2 <= h < 10:
        current = "🌏 Азиатская"
        next_sess = "🇪🇺 Европейская (с 10:00)"
    elif 10 <= h < 16:
        current = "🇪🇺 Европейская"
        next_sess = "🇺🇸 Американская (с 16:00)"
    elif 16 <= h or h < 1:
        current = "🇺🇸 Американская"
        next_sess = "🌏 Азиатская (с 02:00)"
    else:
        current = "🇺🇸 Американская"
        next_sess = "🌏 Азиатская (с 02:00)"
    await update.message.reply_text(
        f"🕗 Сейчас: **{msk.strftime('%H:%M')} (МСК)**\n"
        f"📊 Текущая: **{current}**\n"
        f"🔜 Следующая: **{next_sess}**",
        parse_mode="Markdown"
    )

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
