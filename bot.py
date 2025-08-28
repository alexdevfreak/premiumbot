import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# 🔑 Environment Variables
API_ID = int(os.getenv("API_ID", 123456))  
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))  # your Telegram ID

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
        "👋 Wᴇʟᴄᴏᴍᴇ!\n\n"
        "💖 **Pᴇʀᴍᴀɴᴇɴᴛ Mᴇᴍʙᴇʀsʜɪᴘ – ~₹999~ (Dɪsᴄᴏᴜɴᴛᴇᴅ) ₹499 ⭐**\n\n"
        "✅ Dɪʀᴇᴄᴛ Vɪᴅᴇᴏs Uᴘʟᴏᴀᴅᴇᴅ\n"
        "✅ Dᴀɪʟʏ Nᴇᴡ Uᴘᴅᴀᴛᴇs\n"
        "✅ 10,000+ Vɪᴅᴇᴏs Aʟʀᴇᴀᴅʏ\n"
        "❌ Nᴏ Aᴅs | Nᴏ Lɪɴᴋs\n\n"
        "⚠ Cʜᴇᴄᴋ ᴛʜᴇ Dᴇᴍᴏ Cʜᴀɴɴᴇʟ ʙᴇғᴏʀᴇ ʙᴜʏɪɴɢ.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Pᴀʏ ₹499", callback_data="pay_now")]
        ])
    )

# 💳 Payment Flow
@app.on_callback_query(filters.regex("^pay_now$"))
async def pay_now(_, cb):
    await cb.answer()
    await cb.message.reply_photo(
        photo="https://envs.sh/tsw.jpg",
        caption=(
            "💎 **PAY ₹499 TO GET PREMIUM ACCESS**\n\n"
            "**Scan QR or Pay via UPI:**\n"
            "`BHARATPE.8L0D0N9B3N26276@fbpe`\n\n"
            "> ᴀꜰᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ, sᴇɴᴅ ᴍᴇ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ✅"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Pᴀʏᴍᴇɴᴛ Dᴏɴᴇ", callback_data="payment_done")]
        ])
    )

@app.on_callback_query(filters.regex("^payment_done$"))
async def payment_done(_, cb):
    await cb.answer()
    if cb.from_user.id not in pending_verification:
        pending_verification.add(cb.from_user.id)
        await cb.message.reply_text("📤 Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ ʜᴇʀᴇ.")
    else:
        await cb.message.reply_text("⏳ Yᴏᴜ ᴀʟʀᴇᴀᴅʏ ᴍᴀʀᴋᴇᴅ ᴘᴀʏᴍᴇɴᴛ. Sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ.")

# 📸 Screenshot Handler
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(_, m: Message):
    user = m.from_user
    if user.id not in pending_verification or m.forward_date:
        return

    pending_verification.discard(user.id)  # avoid multiple processing

    time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        f"🧾 **Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ**\n\n"
        f"👤 Nᴀᴍᴇ: {user.first_name}\n"
        f"🔗 Uѕᴇʀɴᴀᴍᴇ: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user.id}\n"
        f"⏰ Tɪᴍᴇ: {time_sent}"
    )

    # Send screenshot once to admin
    await app.send_photo(
        ADMIN_ID,
        photo=m.photo.file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Aᴘᴘʀᴏᴠᴇ", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Rᴇᴊᴇᴄᴛ", callback_data=f"reject_{user.id}")
            ]
        ])
    )

    # Notify user
    await m.reply_text(
        "📸 Yᴏᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴀᴅᴍɪɴ ғᴏʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ.\n\n⏳ Pʟᴇᴀsᴇ ᴡᴀɪᴛ.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="http://t.me/alex_clb")]
        ])
    )

# ✅ Admin Approval
@app.on_callback_query(filters.regex("^approve_"))
async def approve(_, cb):
    user_id = int(cb.data.split("_")[1])
    await app.send_message(
        user_id,
        "🎉 Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! 💎 Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss Hᴀs Bᴇᴇɴ Aᴄᴛɪᴠᴀᴛᴇᴅ\n📂 Jᴏɪɴ Oᴜʀ Sᴇᴄʀᴇᴛ Cʜᴀɴɴᴇʟ",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Jᴏɪɴ Pʀᴇᴍɪᴜᴍ Cʜᴀɴɴᴇʟ", url="https://t.me/Alex_clb")]
        ])
    )
    await cb.answer("User approved ✅")

# ❌ Admin Rejection  
@app.on_callback_query(filters.regex("^reject_"))
async def reject(_, cb):
    user_id = int(cb.data.split("_")[1])
    await app.send_message(
        user_id,
        "❌ Pᴀʏᴍᴇɴᴛ ᴄᴏᴜʟᴅɴ'ᴛ ʙᴇ ᴠᴇʀɪғɪᴇᴅ.\n\nPʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="http://t.me/alex_clb")]
        ])
    )
    await cb.answer("User rejected ❌")

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
@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def user_count(_, m: Message):
    await m.reply(f"👥 Tᴏᴛᴀʟ Uѕᴇʀs: {len(users)}")

# 🆘 /support
@app.on_message(filters.command("support") & filters.private)
async def support(_, m: Message):
    await m.reply_text(
        "📨 Cʜᴀᴛ ᴡɪᴛʜ ᴀᴅᴍɪɴ ᴅɪʀᴇᴄᴛʟʏ.\n\n🆘 Fᴏʀ ʜᴇʟᴘ, ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="http://t.me/alex_clb")]
        ])
    )

# 🟢 Run Bot
print("🤖 Pʀᴇᴍɪᴜᴍ Bᴏᴛ Rᴜɴɴɪɴɢ...")
app.run()
