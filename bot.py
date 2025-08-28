import os
import asyncio
from datetime import datetime
from collections import defaultdict

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ─────────────────────────────────────────────────────────────────────────────
# 🔑 Env Vars (set these in your environment)
# ─────────────────────────────────────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))

# ─────────────────────────────────────────────────────────────────────────────
# 🧠 In-memory data (resets on restart)
# ─────────────────────────────────────────────────────────────────────────────
users = set()                       # all users who hit /start
pending_verification = set()        # users who clicked "Payment Done" and must send screenshot
premium_users = []                  # list of dicts: {id, name, username, date}
verified_or_rejected = set()        # users that already got a final decision (avoid re-approval)

# ─────────────────────────────────────────────────────────────────────────────
# 🚀 Start Bot
# ─────────────────────────────────────────────────────────────────────────────
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────────────────────────────────────
# 👋 /start
# ─────────────────────────────────────────────────────────────────────────────
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
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("💳 Pᴀʏ ₹499", callback_data="pay_now")]]
        ),
        disable_web_page_preview=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 💳 Payment Flow (no double QR)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^pay_now$"))
async def pay_now(_, cb):
    try:
        # Only answer once; do not spam extra messages
        await cb.answer()
        # Send a single QR instruction card
        await cb.message.reply_photo(
            photo="https://envs.sh/tsw.jpg",  # replace with your QR if needed
            caption=(
                "💎 **PAY ₹499 TO GET PREMIUM ACCESS**\n\n"
                "**Scan QR or Pay via UPI:**\n"
                "`BHARATPE.8L0D0N9B3N26276@fbpe`\n\n"
                "> ᴀꜰᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ, sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ✅"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Pᴀʏᴍᴇɴᴛ Dᴏɴᴇ", callback_data="payment_done")]]
            ),
        )
    except Exception as e:
        print(f"Error in pay_now: {e}")
        await cb.answer("Error occurred. Please try again.", show_alert=True)

@app.on_callback_query(filters.regex(r"^payment_done$"))
async def payment_done(_, cb):
    try:
        await cb.answer()
        uid = cb.from_user.id

        # Avoid duplicate prompts: if already queued or decided, don't re-add
        if uid in verified_or_rejected:
            return await cb.message.reply_text("ℹ️ Yᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ʜᴀs ᴀʟʀᴇᴀᴅʏ ʙᴇᴇɴ ʀᴇᴠɪᴇᴡᴇᴅ.")

        if uid not in pending_verification:
            pending_verification.add(uid)
            await cb.message.reply_text(
                "📤 Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ ʜᴇʀᴇ."
            )
        else:
            await cb.message.reply_text("⏳ Aʟʀᴇᴀᴅʏ ᴍᴀʀᴋᴇᴅ. Sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ.")
    except Exception as e:
        print(f"Error in payment_done: {e}")
        await cb.answer("Error occurred. Please try again.", show_alert=True)

# ─────────────────────────────────────────────────────────────────────────────
# 📸 Screenshot Handler
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(_, m: Message):
    try:
        user = m.from_user

        # Ignore if not in verification queue or if the photo is forwarded
        if user.id not in pending_verification or m.forward_date:
            return

        # Move out of pending list now that screenshot is received
        pending_verification.discard(user.id)

        time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption = (
            f"🧾 **Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ**\n\n"
            f"👤 Nᴀᴍᴇ: {user.first_name or 'N/A'}\n"
            f"🔗 Uѕᴇʀɴᴀᴍᴇ: @{user.username or 'N/A'}\n"
            f"🆔 ID: {user.id}\n"
            f"⏰ Tɪᴍᴇ: {time_sent}"
        )

        # Send to admin with Admin-only buttons
        await app.send_photo(
            ADMIN_ID,
            photo=m.photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("✅ Aᴘᴘʀᴏᴠᴇ", callback_data=f"approve_{user.id}"),
                    InlineKeyboardButton("❌ Rᴇᴊᴇᴄᴛ", callback_data=f"reject_{user.id}")
                ]]
            ),
        )

        await m.reply_text(
            "📸 Yᴏᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴀᴅᴍɪɴ ғᴏʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ.\n\n⏳ Pʟᴇᴀsᴇ ᴡᴀɪᴛ.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
            ),
        )
    except Exception as e:
        print(f"Error in handle_screenshot: {e}")
        try:
            await m.reply_text("❌ Error processing screenshot. Please contact support.")
        except:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# ✅ Admin Approval (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.user(ADMIN_ID) & filters.regex(r"^approve_\d+$"))
async def approve(_, cb):
    try:
        await cb.answer("Approved ✅", show_alert=False)
        user_id = int(cb.data.split("_")[1])

        # Avoid duplicate approvals
        if user_id in verified_or_rejected:
            # remove buttons to avoid confusion
            try:
                await cb.message.edit_reply_markup(None)
            except:
                pass
            return

        # Mark final state
        verified_or_rejected.add(user_id)
        pending_verification.discard(user_id)

        # Add buyer info - with better error handling
        try:
            user = await app.get_users(user_id)
            premium_users.append({
                "id": user.id,
                "name": user.first_name or "N/A",
                "username": user.username,
                "date": today_str(),
            })
        except Exception as e:
            print(f"Error getting user info for {user_id}: {e}")
            # Still add to premium users with basic info
            premium_users.append({
                "id": user_id,
                "name": "Unknown User",
                "username": None,
                "date": today_str(),
            })

        # Notify buyer
        try:
            await app.send_message(
                user_id,
                "🎉 Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! 💎 Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss Hᴀs Bᴇᴇɴ Aᴄᴛɪᴠᴀᴛᴇᴅ\n📂 Jᴏɪɴ Oᴜʀ Sᴇᴄʀᴇᴛ Cʜᴀɴɴᴇʟ",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔗 Jᴏɪɴ Pʀᴇᴍɪᴜᴍ Cʜᴀɴɴᴇʟ", url="https://t.me/Alex_clb")]]
                ),
            )
        except Exception as e:
            print(f"Error notifying user {user_id}: {e}")

        # Remove buttons on the admin card (so it can't be clicked again)
        try:
            await cb.message.edit_reply_markup(None)
        except Exception as e:
            print(f"Error removing buttons: {e}")

    except Exception as e:
        print(f"Error in approve: {e}")
        await cb.answer("Error occurred during approval.", show_alert=True)

# ─────────────────────────────────────────────────────────────────────────────
# ❌ Admin Rejection  (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.user(ADMIN_ID) & filters.regex(r"^reject_\d+$"))
async def reject(_, cb):
    try:
        await cb.answer("Rejected ❌", show_alert=False)
        user_id = int(cb.data.split("_")[1])

        # Mark final state
        verified_or_rejected.add(user_id)
        pending_verification.discard(user_id)

        try:
            await app.send_message(
                user_id,
                "❌ Pᴀʏᴍᴇɴᴛ ᴄᴏᴜʟᴅɴ'ᴛ ʙᴇ ᴠᴇʀɪғɪᴇᴅ.\n\nPʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
                ),
            )
        except Exception as e:
            print(f"Error notifying rejected user {user_id}: {e}")

        # Remove buttons on the admin card
        try:
            await cb.message.edit_reply_markup(None)
        except Exception as e:
            print(f"Error removing buttons: {e}")

    except Exception as e:
        print(f"Error in reject: {e}")
        await cb.answer("Error occurred during rejection.", show_alert=True)

# ─────────────────────────────────────────────────────────────────────────────
# 📢 /broadcast  (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(_, m: Message):
    try:
        if not m.reply_to_message:
            return await m.reply("📌 Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.")

        count = 0
        failed = 0
        total_users = len(users)
        
        # Send progress message
        progress_msg = await m.reply(f"📤 Starting broadcast to {total_users} users...")
        
        for uid in list(users):
            try:
                await app.copy_message(uid, m.chat.id, m.reply_to_message.id)
                count += 1
                
                # Update progress every 50 messages
                if count % 50 == 0:
                    try:
                        await progress_msg.edit_text(f"📤 Broadcast progress: {count}/{total_users} sent...")
                    except:
                        pass
                        
            except Exception as e:
                failed += 1
                # silently skip users who blocked the bot or failed delivery
                continue

        await progress_msg.edit_text(f"✅ Bʀᴏᴀᴅᴄᴀsᴛ completed!\n📊 Sent: {count}\n❌ Failed: {failed}")
        
    except Exception as e:
        print(f"Error in broadcast: {e}")
        await m.reply("❌ Error occurred during broadcast.")

# ─────────────────────────────────────────────────────────────────────────────
# 👥 /users (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def user_count(_, m: Message):
    try:
        total_users = len(users)
        pending_count = len(pending_verification)
        premium_count = len(premium_users)
        
        await m.reply(
            f"📊 **Bot Statistics**\n\n"
            f"👥 Total Users: {total_users}\n"
            f"⏳ Pending Verification: {pending_count}\n"
            f"💎 Premium Users: {premium_count}\n"
            f"🗓 Today: {today_str()}"
        )
    except Exception as e:
        print(f"Error in user_count: {e}")
        await m.reply("❌ Error getting user statistics.")

# ─────────────────────────────────────────────────────────────────────────────
# 📊 /listp – Premium Buyers Report (ADMIN ONLY)
#   - Shows per-day group + a "Today" quick counter
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("listp") & filters.user(ADMIN_ID))
async def list_premium(_, m: Message):
    try:
        if not premium_users:
            return await m.reply("📊 Nᴏ ᴘʀᴇᴍɪᴜᴍ ᴘᴜʀᴄʜᴀsᴇs ʏᴇᴛ.")

        # Group by date
        stats = defaultdict(list)
        for u in premium_users:
            stats[u["date"]].append(u)

        today = today_str()
        today_count = len(stats.get(today, []))

        text_lines = []
        text_lines.append("📊 **Premium Buyers Report**")
        text_lines.append(f"🗓 **Today ({today})** → **{today_count}** user(s)\n")

        # Sort dates descending for recent-first report
        for date in sorted(stats.keys(), reverse=True):
            buyers = stats[date]
            text_lines.append(f"📅 {date} → {len(buyers)} user(s)")
            for b in buyers:
                uname = f"@{b['username']}" if b.get("username") else "N/A"
                name = b.get('name', 'N/A') or 'N/A'
                text_lines.append(f"   └ {name} ({uname}) [ID: {b['id']}]")
            text_lines.append("")  # blank line

        # Split message if too long
        full_text = "\n".join(text_lines)
        if len(full_text) > 4096:
            # Send in chunks
            chunks = []
            current_chunk = ""
            
            for line in text_lines:
                if len(current_chunk + line + "\n") > 4000:
                    chunks.append(current_chunk)
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
            
            if current_chunk:
                chunks.append(current_chunk)
            
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await m.reply(chunk)
                else:
                    await m.reply(f"**Report continued ({i+1}/{len(chunks)})**\n\n{chunk}")
        else:
            await m.reply(full_text)
            
    except Exception as e:
        print(f"Error in list_premium: {e}")
        await m.reply("❌ Error generating premium users report.")

# ─────────────────────────────────────────────────────────────────────────────
# 🆘 /support
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("support") & filters.private)
async def support(_, m: Message):
    await m.reply_text(
        "📨 Cʜᴀᴛ ᴡɪᴛʜ ᴀᴅᴍɪɴ ᴅɪʀᴇᴄᴛʟʏ.\n\n🆘 Fᴏʀ ʜᴇʟᴘ, ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
        ),
        disable_web_page_preview=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 🟢 Run Bot
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 Pʀᴇᴍɪᴜᴍ Bᴏᴛ Starting...")
    try:
        app.run()
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
