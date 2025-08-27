import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# 🔑 Environment Variables
API_ID = int(os.getenv("API_ID", 12870719))
API_HASH = os.getenv("API_HASH", "aec3e63c5538ca578429174d6769b3ac")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8328426081:AAGo_cgQWL2_qGQW2ibGyD_tJFud-Th-cyc")
ADMIN_ID = int(os.getenv("ADMIN_ID", 7202273962))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", -1002649126743))

# 🧠 User Database
users = set()

# 🚀 Start Bot
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 👋 /start
@app.on_message(filters.command("start"))
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
    await cb.message.reply_text("📤 Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ.")

# 📸 Screenshot Handler
@app.on_message(filters.photo)
async def handle_screenshot(_, m: Message):
    user = m.from_user
    time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        f"🧾 Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ\n\n"
        f"👤 Nᴀᴍᴇ: {user.first_name}\n"
        f"🔗 Uѕᴇʀɴᴀᴍᴇ: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user.id}\n"
        f"⏰ Tɪᴍᴇ: {time_sent}"
    )
    await m.forward(ADMIN_ID)
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
    await m.reply("📨 Sᴄʀᴇᴇɴsʜᴏᴛ sᴇɴᴛ ғᴏʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ.")

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
        "❌ Sᴏʀʀʏ, ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ᴡᴀs ɴᴏᴛ ᴠᴀʟɪᴅᴀᴛᴇᴅ. Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
    )
    await cb.answer("User rejected ❌")

# 🛠 /support
@app.on_message(filters.command("support"))
async def support(_, m: Message):
    await m.reply_text(
        "📨 Msɢ ʜᴇʀᴇ ᴛᴏ ᴄʜᴀᴛ ᴡɪᴛʜ ᴛʜᴇ ᴀᴅᴍɪɴ",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="http://t.me/alex_clb?&text=Sᴜᴘᴘᴏʀᴛ")]
        ])
    )

# 📢 /broadcast (admin only)
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(_, m: Message):
    if not m.reply_to_message:
        return await m.reply("📌 Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.")
    count = 0
    for uid in users:
        try:
            await app.copy_message(uid, m.chat.id, m.reply_to_message.id)
            count += 1
        except:
            continue
    await m.reply(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ sᴇɴᴛ ᴛᴏ {count} ᴜsᴇʀs.")

# 👥 /users
@app.on_message(filters.command("users"))
async def user_count(_, m: Message):
    await m.reply(f"👥 Tᴏᴛᴀʟ Rᴇɢɪsᴛᴇʀᴇᴅ Uѕᴇʀs: {len(users)}")

# 🟢 Run Bot
print("🤖 Pʀᴇᴍɪᴜᴍ Bᴏᴛ Rᴜɴɴɪɴɢ...")
app.run()
