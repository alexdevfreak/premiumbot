import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# 🔑 Environment Variables
API_ID = int(os.getenv("API_ID", 12870719))
API_HASH = os.getenv("API_HASH", "aec3e63c5538ca578429174d6769b3ac")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8328426081:AAGo_cgQWL2_qGQW2ibGyD_tJFud-Th-cyc")
ADMIN_ID = int(os.getenv("ADMIN_ID", 7202273962))

# 🧠 In-memory user tracking
users = set()
pending_verification = set()

# 🚀 Start Bot
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 👋 /start
@app.on_message(filters.command("start") & filters.private)
async def start(_, m: Message):
    users.add(m.from_user.id)
    await m.reply_text(
        "👋 Wᴇʟᴄᴏᴍᴇ! 💎 Bᴜʏ Pʀᴇᴍɪᴜᴍ ғᴏʀ ᴊᴏɪɴɪɴɢ ᴏᴜʀ sᴇᴄʀᴇᴛ ᴄʜᴀɴɴᴇʟ 💰 Pʀɪᴄᴇ: 499",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Pᴀʏ 499", callback_data="pay_now")]
        ])
    )

# 💳 Payment Flow
@app.on_callback_query(filters.regex("pay_now"))
async def pay_now(_, cb):
    await cb.message.reply_photo(
        photo="https://envs.sh/tsw.jpg/jfals.Zip_Extractor_Robot",
        caption="📸 Sᴄᴀɴ Qʀ ᴄᴏᴅᴇ ᴛᴏ ᴘᴀʏ 499.\n\nAғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ, ᴄʟɪᴄᴋ 'Pᴀʏᴍᴇɴᴛ Dᴏɴᴇ'",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Pᴀʏᴍᴇɴᴛ Dᴏɴᴇ", callback_data="payment_done")]
        ])
    )

@app.on_callback_query(filters.regex("payment_done"))
async def payment_done(_, cb):
    pending_verification.add(cb.from_user.id)
    await cb.message.reply_text(
        "📤 Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ ʜᴇʀᴇ."
    )

# 📸 Screenshot Handler
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(_, m: Message):
    user = m.from_user
    if user.id not in pending_verification or m.forward_date:
        return

    pending_verification.discard(user.id)
    time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        f"🧾 Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ\n\n"
        f"👤 Nᴀᴍᴇ: {user.first_name}\n"
        f"🔗 Uѕᴇʀɴᴀᴍᴇ: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user.id}\n"
        f"⏰ Tɪᴍᴇ: {time_sent}"
    )

    await m.forward(ADMIN_ID)

    await m.reply_text(
        "📸 Yᴏᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ!\n\n🕵️‍♂️ Iᴛ ʜᴀs ʙᴇᴇɴ ғᴏʀᴡᴀʀᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴ ғᴏʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ.\n⏳ Pʟᴇᴀsᴇ ᴡᴀɪᴛ ᴘᴀᴛɪᴇɴᴛʟʏ.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="http://t.me/alex_clb?&text=Sᴜᴘᴘᴏʀᴛ")]
        ])
    )

    await app.send_message(
        ADMIN_ID,
        caption,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Aᴘᴘʀᴏᴠᴇ", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Rᴇᴊᴇᴄᴛ", callback_data=f"reject_{user.id}")
            ]
        ])
    )

# ✅ Admin Approval
@app.on_callback_query(filters.regex("approve_"))
async def approve(_, cb):
    user_id = int(cb.data.split("_")[1])
    await app.send_message(
        user_id,
        "🎉 Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! 💎 Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss Hᴀs Bᴇᴇɴ Aᴄᴛɪᴠᴀᴛᴇᴅ 📂 Jᴏɪɴ Oᴜʀ Sᴇᴄʀᴇᴛ Cʜᴀɴɴᴇʟ",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Jᴏɪɴ Pʀᴇᴍɪᴜᴍ Cʜᴀɴɴᴇʟ", url="https://t.me/Alex_clb")]
        ])
    )
    await cb.answer("User approved ✅")

@app.on_callback_query(filters.regex("reject_"))
async def reject(_, cb):
    user_id = int(cb.data.split("_")[1])
    await app.send_message(
        user_id,
        "❌ Sᴏʀʀʏ, ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ᴡᴀs ɴᴏᴛ ᴠᴀʟɪᴅᴀᴛᴇᴅ.\n🆘 Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ғᴏʀ ᴀssɪsᴛᴀɴᴄᴇ."
    )
    await cb.answer("User rejected ❌")

# 🛠 /support
@app.on_message(filters.command("support") & filters.private)
async def support(_,
