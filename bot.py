import os
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔑 Environment Variables (from Render dashboard → Environment)
API_ID = int(os.getenv("API_ID", "123456"))  
API_HASH = os.getenv("API_HASH", "your_api_hash")  
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  

LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1001234567890"))
DATA_CHANNEL = int(os.getenv("DATA_CHANNEL", "-1001234567890"))

# 🎭 Start Bot
app = Client(
    "premiumbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 🟢 /start command
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "👋 𝐇𝐞𝐲! 𝐈'𝐦 𝐲𝐨𝐮𝐫 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐅𝐢𝐥𝐞 𝐒𝐭𝐨𝐫𝐞 𝐁𝐨𝐭.\n\n"
        "📂 𝐒𝐞𝐧𝐝 𝐦𝐞 𝐚𝐧𝐲 𝐟𝐢𝐥𝐞, 𝐚𝐧𝐝 𝐈’𝐥𝐥 𝐠𝐢𝐯𝐞 𝐲𝐨𝐮 𝐚 𝐬𝐡𝐚𝐫𝐚𝐛𝐥𝐞 𝐥𝐢𝐧𝐤."
    )

# 📤 Store file
@app.on_message(filters.document | filters.video | filters.photo)
async def store_file(_, m: Message):
    file = m.document or m.video or m.photo
    file_id = file.file_id  

    # Forward to data channel
    sent = await m.forward(DATA_CHANNEL)

    # Make sharable link
    link = f"https://t.me/{app.me.username}?start={sent.id}"

    await m.reply_text(
        f"✅ 𝐅𝐢𝐥𝐞 𝐒𝐚𝐯𝐞𝐝!\n\n📥 [𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞 𝐭𝐨 𝐆𝐞𝐭 𝐘𝐨𝐮𝐫 𝐅𝐢𝐥𝐞]({link})",
        disable_web_page_preview=True
    )

# 🟢 Run Bot
print("🤖 Bot Running...")
app.run()
