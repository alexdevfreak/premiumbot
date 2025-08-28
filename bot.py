import os
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

# Payment QR (global)
PAYMENT_QR = "https://envs.sh/tsw.jpg/jfals.Zip_Extractor_Robot"
UPI_ID = "BHARATPE.8L0D0N9B3N26276@fbpe"

# Premium counter file
COUNTER_FILE = "premium_counter.json"

# ================= BOT =================
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= STORAGE HELPERS =================
def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {}
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counter(data):
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def increment_today_count():
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_counter()
    data[today] = data.get(today, 0) + 1
    save_counter(data)

# ================= COMMANDS =================
@app.on_message(filters.command("start"))
async def start(_, m):
    await m.reply_text(
        "👋 Welcome to *Premium Bot*!\n\n"
        "✨ Unlock exclusive access by upgrading to premium.",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("💳 Buy Premium", callback_data="pay_now")]]
        ),
    )

@app.on_message(filters.command("listp"))
async def listp(_, m):
    data = load_counter()
    if not data:
        await m.reply_text("📊 No premium purchases yet.")
        return

    msg = "📊 *Premium Purchases Count:*\n\n"
    for date, count in sorted(data.items()):
        msg += f"📅 {date} → {count} users\n"

    await m.reply_text(msg, parse_mode="markdown")

# ================= PAYMENT FLOW =================
@app.on_callback_query(filters.regex("^pay_now$"))
async def pay_now(_, cb):
    await cb.answer()
    caption = (
        "💎 *PAY HERE TO GET PREMIUM ACCESS*\n\n"
        f"📷 Scan QR or pay via UPI:\n`{UPI_ID}`\n\n"
        "⚡ After payment, send your screenshot here."
    )
    await cb.message.reply_photo(
        photo=PAYMENT_QR,
        caption=caption,
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")]]
        ),
    )

@app.on_callback_query(filters.regex("^retry_payment$"))
async def retry_payment(_, cb):
    await cb.answer()
    caption = (
        "⚠️ *Payment not detected.*\n\n"
        f"👉 Please try again:\n`{UPI_ID}`\n\n"
        "📷 Scan QR below ⬇️"
    )
    await cb.message.reply_photo(
        photo=PAYMENT_QR,
        caption=caption,
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")]]
        ),
    )

@app.on_callback_query(filters.regex("^payment_done$"))
async def payment_done(_, cb):
    await cb.answer()
    increment_today_count()
    await cb.message.reply_text(
        "✅ *Thank you!* Your payment has been marked.\n\n"
        "⏳ Please wait while we verify your transaction.",
        parse_mode="markdown",
    )

# ================= RUN =================
print("🚀 Bot started...")
app.run()

