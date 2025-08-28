import os
from datetime import datetime
from collections import defaultdict

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# ─────────────────────────────────────────────────────────────────────────────
# 🔑 Env Vars (set these in your environment)
# ─────────────────────────────────────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))

# Replace this with a valid direct image URL or a Telegram file_id
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "https://example.com/qr.jpg")

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
    if not m.from_user:
        return
    users.add(m.from_user.id)

    text = (
        "👋 WELCOME!\n\n"
        "💖 PERMANENT MEMBERSHIP – ~₹999~ (DISCOUNTED) ₹499 ⭐\n\n"
        "✅ Direct videos uploaded\n"
        "✅ Daily new updates\n"
        "✅ 10,000+ videos already\n"
        "❌ No ads | No links\n\n"
        "⚠ Check the demo channel before buying."
    )

    await m.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("💳 Pay ₹499", callback_data="pay_now")]]
        ),
        disable_web_page_preview=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 💳 Payment Flow (no double QR)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^pay_now$"))
async def pay_now(_, cb):
    await cb.answer()
    try:
        caption = (
            "PAY ₹499 TO GET PREMIUM ACCESS\n\n"
            "Scan QR or pay via UPI:\n"
            "BHARATPE.8L0D0N9B3N26276@fbpe\n\n"
            "After payment, please send a screenshot of your payment receipt here."
        )
        await cb.message.reply_photo(
            photo=QR_IMAGE_URL,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")]]
            ),
        )
    except Exception:
        # fallback: send as text if photo fails
        await cb.message.reply_text(
            "PAY ₹499 TO GET PREMIUM ACCESS\n\n"
            "UPI: BHARATPE.8L0D0N9B3N26276@fbpe\n\n"
            "After payment, send a screenshot here.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")]]
            ),
        )

@app.on_callback_query(filters.regex(r"^payment_done$"))
async def payment_done(_, cb):
    await cb.answer()
    uid = cb.from_user.id

    # Avoid duplicate prompts: if already queued or decided, don't re-add
    if uid in verified_or_rejected:
        return await cb.message.reply_text("Info: Your payment was already reviewed.")

    if uid not in pending_verification:
        pending_verification.add(uid)
        await cb.message.reply_text(
            "Please send a screenshot of your payment receipt here (do not forward)."
        )
    else:
        await cb.message.reply_text("You are already marked as pending. Please send the screenshot.")

# ─────────────────────────────────────────────────────────────────────────────
# 📸 Screenshot Handler
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(_, m: Message):
    user = m.from_user
    if not user:
        return

    # Ignore if not in verification queue or if the photo is forwarded
    if user.id not in pending_verification or m.forward_date:
        return

    # Move out of pending list now that screenshot is received
    pending_verification.discard(user.id)

    time_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        f"PAYMENT SCREENSHOT\n\n"
        f"Name: {user.first_name}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"ID: {user.id}\n"
        f"Time: {time_sent}"
    )

    # Send to admin with Admin-only buttons
    try:
        await app.send_photo(
            ADMIN_ID,
            photo=m.photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
                ]]
            ),
        )
    except Exception:
        # If admin photo send fails, send message instead
        try:
            await app.send_message(
                ADMIN_ID,
                caption,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
                        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
                    ]]
                ),
            )
        except Exception:
            pass

    await m.reply_text(
        "Your screenshot has been sent to admin for verification. Please wait a little while.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Contact Support", url="https://t.me/alex_clb")]]
        ),
    )

# ─────────────────────────────────────────────────────────────────────────────
# ✅ Admin Approval (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.user(ADMIN_ID) & filters.regex(r"^approve_\d+$"))
async def approve(_, cb):
    await cb.answer("Approved", show_alert=False)
    user_id = int(cb.data.split("_")[1])

    # Avoid duplicate approvals
    if user_id in verified_or_rejected:
        try:
            await cb.message.edit_reply_markup(None)
        except Exception:
            pass
        return

    # Mark final state
    verified_or_rejected.add(user_id)
    pending_verification.discard(user_id)

    # Try fetching user info; if it fails, still store ID and date
    try:
        user = await app.get_users(user_id)
        name = user.first_name if getattr(user, "first_name", None) else "Unknown"
        username = user.username if getattr(user, "username", None) else None
    except Exception:
        name = "Unknown"
        username = None

    premium_users.append({
        "id": user_id,
        "name": name,
        "username": username,
        "date": today_str(),
    })

    # Notify buyer
    try:
        await app.send_message(
            user_id,
            "Congratulations! Your premium access has been activated. Join the premium channel.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join Premium Channel", url="https://t.me/Alex_clb")]]
            ),
        )
    except Exception:
        pass

    # Remove buttons on the admin card (so it can’t be clicked again)
    try:
        await cb.message.edit_reply_markup(None)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# ❌ Admin Rejection  (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.user(ADMIN_ID) & filters.regex(r"^reject_\d+$"))
async def reject(_, cb):
    await cb.answer("Rejected", show_alert=False)
    user_id = int(cb.data.split("_")[1])

    # Mark final state
    verified_or_rejected.add(user_id)
    pending_verification.discard(user_id)

    try:
        await app.send_message(
            user_id,
            "Sorry, your payment could not be verified. Please contact support.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url="https://t.me/alex_clb")]]
            ),
        )
    except Exception:
        pass

    # Remove buttons on the admin card
    try:
        await cb.message.edit_reply_markup(None)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# 📢 /broadcast  (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(_, m: Message):
    if not m.reply_to_message:
        return await m.reply("Reply to a message to broadcast it.")

    count = 0
    for uid in list(users):
        try:
            await app.copy_message(uid, m.chat.id, m.reply_to_message.id)
            count += 1
        except Exception:
            continue

    await m.reply(f"Broadcast sent to {count} users.")

# ─────────────────────────────────────────────────────────────────────────────
# 👥 /users (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def user_count(_, m: Message):
    await m.reply(f"Total users: {len(users)}")

# ─────────────────────────────────────────────────────────────────────────────
# 📊 /listp – Premium Buyers Report (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("listp") & filters.user(ADMIN_ID))
async def list_premium(_, m: Message):
    if not premium_users:
        return await m.reply("No premium purchases yet.")

    # Group by date
    stats = defaultdict(list)
    for u in premium_users:
        stats[u["date"]].append(u)

    today = today_str()
    today_count = len(stats.get(today, []))

    text_lines = []
    text_lines.append("Premium Buyers Report")
    text_lines.append(f"Today ({today}) → {today_count} user(s)\n")

    # Sort dates descending for recent-first report
    for date in sorted(stats.keys(), reverse=True):
        buyers = stats[date]
        text_lines.append(f"{date} → {len(buyers)} user(s)")
        for b in buyers:
            uname = f"@{b['username']}" if b.get("username") else "N/A"
            text_lines.append(f"  - {b['name']} ({uname}) [ID: {b['id']}]")
        text_lines.append("")  # blank line

    await m.reply("\n".join(text_lines))

# ─────────────────────────────────────────────────────────────────────────────
# 🆘 /support
# ─────────────────────────────────────────────────────────────────────────────
@app.on_message(filters.command("support") & filters.private)
async def support(_, m: Message):
    await m.reply_text(
        "Chat with admin directly for support.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Support", url="https://t.me/alex_clb")]]
        ),
        disable_web_page_preview=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 🟢 Run Bot
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Premium bot running...")
    app.run()
