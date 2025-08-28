import os
from datetime import datetime
from collections import defaultdict

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ─────────────────────────────────────────────────────────────────────────────
# 🔑 Environment Variables
# ─────────────────────────────────────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))

# ─────────────────────────────────────────────────────────────────────────────
# 🧠 Data Storage
# ─────────────────────────────────────────────────────────────────────────────
users = set()
pending_verification = set()
premium_users = []
verified_or_rejected = set()
admin_ids = {ADMIN_ID}
user_states = {}  # Track user states properly

# ─────────────────────────────────────────────────────────────────────────────
# 🚀 Bot Client
# ─────────────────────────────────────────────────────────────────────────────
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def is_admin(user_id):
    return user_id in admin_ids

# ─────────────────────────────────────────────────────────────────────────────
# 👋 /start Command
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start(_, m):
    users.add(m.from_user.id)
    user_states[m.from_user.id] = "start"

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
# 💳 Pay Now Callback
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^pay_now$"))
async def pay_now(_, cb):
    user_id = cb.from_user.id
    
    # Prevent double QR sending
    if user_states.get(user_id) == "qr_sent":
        await cb.answer("QR already sent! Check above messages.", show_alert=True)
        return
        
    await cb.answer()
    user_states[user_id] = "qr_sent"
    
    await cb.message.reply_photo(
        photo="https://envs.sh/tsw.jpg/jfals.Zip_Extractor_Robot",
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

# ─────────────────────────────────────────────────────────────────────────────
# ✅ Payment Done Callback  
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^payment_done$"))
async def payment_done(_, cb):
    user_id = cb.from_user.id
    
    if user_id in verified_or_rejected:
        await cb.answer("Your payment has already been reviewed.", show_alert=True)
        return
    
    if user_states.get(user_id) == "payment_marked":
        await cb.answer("Already marked! Send your screenshot.", show_alert=True)
        return
        
    await cb.answer("📤 Now send your payment screenshot here!", show_alert=True)
    user_states[user_id] = "payment_marked"
    pending_verification.add(user_id)

# ─────────────────────────────────────────────────────────────────────────────
# 📸 Screenshot Handler
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(_, m):
    user = m.from_user
    user_id = user.id
    
    # Only process if user marked payment as done
    if user_states.get(user_id) != "payment_marked":
        return
        
    if m.forward_date:
        return

    # Prevent double processing
    if user_states.get(user_id) == "screenshot_sent":
        return
        
    user_states[user_id] = "screenshot_sent"
    pending_verification.discard(user_id)

    time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        f"🧾 **Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ**\n\n"
        f"👤 Nᴀᴍᴇ: {user.first_name or 'N/A'}\n"
        f"🔗 Uѕᴇʀɴᴀᴍᴇ: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user.id}\n"
        f"⏰ Tɪᴍᴇ: {time_sent}"
    )

    # Send to all admins
    for admin_id in admin_ids:
        try:
            await app.send_photo(
                admin_id,
                photo=m.photo.file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Aᴘᴘʀᴏᴠᴇ", callback_data=f"approve_{user.id}"),
                        InlineKeyboardButton("❌ Rᴇᴊᴇᴄᴛ", callback_data=f"reject_{user.id}")
                    ]
                ]),
            )
        except:
            continue

    # Send single confirmation to user
    await m.reply_text(
        "📸 Yᴏᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴀᴅᴍɪɴ ғᴏʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ.\n\n⏳ Pʟᴇᴀsᴇ ᴡᴀɪᴛ.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
        ),
    )

# ─────────────────────────────────────────────────────────────────────────────
# ✅ Admin Approval
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^approve_\d+$"))
async def approve(_, cb):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ Not authorized!", show_alert=True)
        return

    await cb.answer("Approved ✅")
    user_id = int(cb.data.split("_")[1])

    if user_id in verified_or_rejected:
        await cb.message.edit_reply_markup(None)
        return

    verified_or_rejected.add(user_id)
    pending_verification.discard(user_id)
    user_states[user_id] = "approved"

    try:
        user = await app.get_users(user_id)
        premium_users.append({
            "id": user.id,
            "name": user.first_name or "N/A",
            "username": user.username,
            "date": today_str(),
        })
    except:
        premium_users.append({
            "id": user_id,
            "name": "Unknown User",
            "username": None,
            "date": today_str(),
        })

    try:
        await app.send_message(
            user_id,
            "🎉 Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! 💎 Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss Hᴀs Bᴇᴇɴ Aᴄᴛɪᴠᴀᴛᴇᴅ\n📂 Jᴏɪɴ Oᴜʀ Sᴇᴄʀᴇᴛ Cʜᴀɴɴᴇʟ",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Jᴏɪɴ Pʀᴇᴍɪᴜᴍ Cʜᴀɴɴᴇʟ", url="https://t.me/Alex_clb")]]
            ),
        )
    except:
        pass

    await cb.message.edit_reply_markup(None)

# ─────────────────────────────────────────────────────────────────────────────
# ❌ Admin Rejection
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^reject_\d+$"))
async def reject(_, cb):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ Not authorized!", show_alert=True)
        return

    await cb.answer("Rejected ❌")
    user_id = int(cb.data.split("_")[1])

    verified_or_rejected.add(user_id)
    pending_verification.discard(user_id)
    user_states[user_id] = "rejected"

    try:
        await app.send_message(
            user_id,
            "❌ Pᴀʏᴍᴇɴᴛ ᴄᴏᴜʟᴅɴ'ᴛ ʙᴇ ᴠᴇʀɪғɪᴇᴅ.\n\nPʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🆘 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
            ),
        )
    except:
        pass

    await cb.message.edit_reply_markup(None)

# ─────────────────────────────────────────────────────────────────────────────
# 👤 /addadmin - Add Staff Admin (Main Admin Only)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("addadmin") & filters.user(ADMIN_ID))
async def add_admin(_, m):
    if len(m.command) != 2:
        return await m.reply("❌ **Usage:** `/addadmin USER_ID`")
    
    try:
        new_admin_id = int(m.command[1])
    except ValueError:
        return await m.reply("❌ **Invalid User ID!**")
    
    if new_admin_id in admin_ids:
        return await m.reply("ℹ️ **User is already an admin!**")
    
    try:
        user = await app.get_users(new_admin_id)
        admin_ids.add(new_admin_id)
        
        await m.reply(
            f"✅ **New Admin Added!**\n\n"
            f"👤 **Name:** {user.first_name or 'N/A'}\n"
            f"🔗 **Username:** @{user.username or 'N/A'}\n"
            f"🆔 **ID:** `{user.id}`\n\n"
            f"📊 **Total Admins:** {len(admin_ids)}"
        )
        
        try:
            await app.send_message(
                new_admin_id,
                "🎉 **You are now an Admin/Staff!**\n\n"
                "✅ **You can now:**\n"
                "• Approve/Reject payments\n"
                "• View statistics with `/users`\n"
                "• View premium users with `/listp`\n"
                "• Send broadcasts with `/broadcast`\n\n"
                "⚠️ **Note:** Only main admin can add/remove admins."
            )
        except:
            pass
            
    except:
        await m.reply("❌ **User not found!**")

# ─────────────────────────────────────────────────────────────────────────────
# 👥 /listadmins - List All Admins (Main Admin Only)  
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("listadmins") & filters.user(ADMIN_ID))
async def list_admins(_, m):
    text_lines = ["👥 **Admin List:**\n"]
    
    for i, admin_id in enumerate(admin_ids, 1):
        try:
            user = await app.get_users(admin_id)
            admin_type = "🔴 **Main**" if admin_id == ADMIN_ID else "🟢 **Staff**"
            text_lines.append(
                f"{i}. {admin_type}\n"
                f"   └ {user.first_name or 'N/A'} (@{user.username or 'N/A'})\n"
                f"   └ ID: `{admin_id}`\n"
            )
        except:
            admin_type = "🔴 **Main**" if admin_id == ADMIN_ID else "🟢 **Staff**"  
            text_lines.append(f"{i}. {admin_type} - ID: `{admin_id}`\n")
    
    text_lines.append(f"\n📊 **Total:** {len(admin_ids)}")
    await m.reply("\n".join(text_lines))

# ─────────────────────────────────────────────────────────────────────────────
# 🗑️ /removeadmin - Remove Staff Admin (Main Admin Only)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("removeadmin") & filters.user(ADMIN_ID))
async def remove_admin(_, m):
    if len(m.command) != 2:
        return await m.reply("❌ **Usage:** `/removeadmin USER_ID`")
    
    try:
        admin_to_remove = int(m.command[1])
    except ValueError:
        return await m.reply("❌ **Invalid User ID!**")
    
    if admin_to_remove == ADMIN_ID:
        return await m.reply("❌ **Cannot remove main admin!**")
    
    if admin_to_remove not in admin_ids:
        return await m.reply("❌ **User is not an admin!**")
    
    admin_ids.discard(admin_to_remove)
    await m.reply(f"✅ **Admin removed!** Remaining: {len(admin_ids)}")
    
    try:
        await app.send_message(
            admin_to_remove,
            "📢 **Admin access removed.** Thank you for your service!"
        )
    except:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# 📢 /broadcast (All Admins)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("broadcast"))
async def broadcast(_, m):
    if not is_admin(m.from_user.id):
        return await m.reply("❌ **Not authorized!**")
        
    if not m.reply_to_message:
        return await m.reply("📌 **Reply to a message to broadcast.**")

    count = 0
    total_users = len(users)
    
    progress_msg = await m.reply(f"📤 **Broadcasting to {total_users} users...**")
    
    for uid in users:
        try:
            await app.copy_message(uid, m.chat.id, m.reply_to_message.id)
            count += 1
        except:
            continue

    await progress_msg.edit_text(f"✅ **Broadcast completed!** Sent to {count} users.")

# ─────────────────────────────────────────────────────────────────────────────
# 👥 /users (All Admins)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("users"))
async def user_count(_, m):
    if not is_admin(m.from_user.id):
        return await m.reply("❌ **Not authorized!**")
        
    await m.reply(
        f"📊 **Bot Statistics**\n\n"
        f"👥 **Total Users:** {len(users)}\n"
        f"⏳ **Pending:** {len(pending_verification)}\n"  
        f"💎 **Premium:** {len(premium_users)}\n"
        f"👤 **Admins:** {len(admin_ids)}\n"
        f"🗓 **Date:** {today_str()}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 📊 /listp - Premium Users Report (All Admins)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("listp"))
async def list_premium(_, m):
    if not is_admin(m.from_user.id):
        return await m.reply("❌ **Not authorized!**")
        
    if not premium_users:
        return await m.reply("📊 **No premium purchases yet.**")

    stats = defaultdict(list)
    for u in premium_users:
        stats[u["date"]].append(u)

    today = today_str()
    today_count = len(stats.get(today, []))

    text_lines = ["📊 **Premium Buyers Report**", f"🗓 **Today ({today}):** {today_count}\n"]

    for date in sorted(stats.keys(), reverse=True):
        buyers = stats[date]
        text_lines.append(f"📅 **{date}** - {len(buyers)} users")
        for b in buyers:
            uname = f"@{b['username']}" if b.get("username") else "N/A"
            name = b.get('name', 'N/A') or 'N/A'
            text_lines.append(f"   └ {name} ({uname}) [`{b['id']}`]")
        text_lines.append("")

    full_text = "\n".join(text_lines)
    
    if len(full_text) > 4096:
        for i in range(0, len(full_text), 4000):
            await m.reply(full_text[i:i+4000])
    else:
        await m.reply(full_text)

# ─────────────────────────────────────────────────────────────────────────────
# 🆘 /support
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("support") & filters.private)
async def support(_, m):
    await m.reply_text(
        "📨 Cʜᴀᴛ ᴡɪᴛʜ ᴀᴅᴍɪɴ ᴅɪʀᴇᴄᴛʟʏ.\n\n🆘 Fᴏʀ ʜᴇʟᴘ, ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🆘 Sᴜᴘᴘᴏʀᴛ", url="https://t.me/alex_clb")]]
        ),
    )

# ─────────────────────────────────────────────────────────────────────────────
# 🟢 Run Bot
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 Premium Bot Starting...")
    app.run()
