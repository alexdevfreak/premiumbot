#!/usr/bin/env python3
"""
Premium Bot - Copy/paste ready.

Features:
- No double messages anywhere (QR-only payment flows).
- Global QR link used consistently.
- SQLite persistence for users, pending verification, premium buyers.
- Admin-only approve/reject with prevention of duplicate approvals.
- /listp admin-only with per-day breakdown and buyer details.
- /users, /broadcast (admin-only), /support, /start, /help.
- Simple logging to stdout.
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Optional, Tuple, List

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# -------------------------
# Configuration (env vars)
# -------------------------
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Global payment/QR configuration
PAYMENT_QR = os.getenv(
    "PAYMENT_QR",
    "https://envs.sh/tsw.jpg/jfals.Zip_Extractor_Robot",
)
UPI_ID = os.getenv("UPI_ID", "BHARATPE.8L0D0N9B3N26276@fbpe")

# Database file
DB_FILE = os.getenv("DB_FILE", "premium_bot.db")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | %(message)s",
)
logger = logging.getLogger("premium_bot")

# -------------------------
# Utility helpers
# -------------------------
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

# -------------------------
# Database (SQLite) object
# -------------------------
class DB:
    def __init__(self, path: str):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        cur = self._conn.cursor()
        # users table: stores users who hit /start (optional)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                last_seen TEXT
            );
            """
        )
        # pending_verifications table: stores user_id + timestamp + file_id
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_verifications (
                user_id INTEGER PRIMARY KEY,
                requested_at TEXT,
                file_id TEXT
            );
            """
        )
        # premium_buyers table: stores approved buyers
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS premium_buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                approved_at TEXT,
                admin_id INTEGER
            );
            """
        )
        self._conn.commit()

    # user functions
    def add_or_update_user(self, uid: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]):
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO users (id, username, first_name, last_name, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                last_seen=excluded.last_seen
            ;
            """,
            (uid, username, first_name, last_name, now_str()),
        )
        self._conn.commit()

    def get_all_user_ids(self) -> List[int]:
        cur = self._conn.cursor()
        cur.execute("SELECT id FROM users;")
        return [row["id"] for row in cur.fetchall()]

    def get_user(self, uid: int) -> Optional[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?;", (uid,))
        return cur.fetchone()

    # pending verification functions
    def mark_pending(self, uid: int, file_id: Optional[str] = None):
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO pending_verifications (user_id, requested_at, file_id)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                requested_at=excluded.requested_at,
                file_id=excluded.file_id
            ;
            """,
            (uid, now_str(), file_id or ""),
        )
        self._conn.commit()

    def set_pending_file(self, uid: int, file_id: str):
        cur = self._conn.cursor()
        cur.execute("UPDATE pending_verifications SET file_id=? WHERE user_id=?;", (file_id, uid))
        self._conn.commit()

    def remove_pending(self, uid: int):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM pending_verifications WHERE user_id=?;", (uid,))
        self._conn.commit()

    def get_pending(self, uid: int) -> Optional[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM pending_verifications WHERE user_id=?;", (uid,))
        return cur.fetchone()

    def get_all_pending(self) -> List[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM pending_verifications;")
        return cur.fetchall()

    # premium buyers functions
    def add_premium_buyer(self, uid: int, username: Optional[str], first_name: Optional[str], admin_id: int):
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO premium_buyers (user_id, username, first_name, approved_at, admin_id)
            VALUES (?, ?, ?, ?, ?);
            """,
            (uid, username or "", first_name or "", now_str(), admin_id),
        )
        self._conn.commit()

    def is_premium(self, uid: int) -> bool:
        cur = self._conn.cursor()
        cur.execute("SELECT 1 FROM premium_buyers WHERE user_id=? LIMIT 1;", (uid,))
        return cur.fetchone() is not None

    def get_premium_by_date(self) -> dict:
        """
        Returns dict: { 'YYYY-MM-DD': [rows...] }
        """
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM premium_buyers ORDER BY approved_at DESC;")
        rows = cur.fetchall()
        out = {}
        for r in rows:
            date_only = r["approved_at"][:10]  # YYYY-MM-DD from ISO
            out.setdefault(date_only, []).append(r)
        return out

    def get_premium_count_today(self) -> int:
        today = today_date_str()
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM premium_buyers WHERE approved_at LIKE ?;", (today + "%",))
        r = cur.fetchone()
        return r["c"] if r else 0

# create DB
db = DB(DB_FILE)

# -------------------------
# Bot initialization
# -------------------------
app = Client("premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------------
# Keyboard buttons (reused)
# -------------------------
def main_buy_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💳 Pay ₹499", callback_data="pay_now")]]
    )

def qr_payment_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")]]
    )

def admin_verify_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ])

support_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🆘 Contact Support", url="https://t.me/alex_clb")]]
)

# -------------------------
# Helper: send single QR-only message (no text fallback)
# -------------------------
async def send_payment_qr_only(target, caption: str, reply_markup=None):
    """
    Send only the QR image with caption. 'target' may be a Message object (reply target) or chat_id.
    Always uses PAYMENT_QR; no text fallback is sent.
    """
    # target can be a Message -> reply_photo; or chat_id -> send_photo
    if isinstance(target, Message):
        await target.reply_photo(
            photo=PAYMENT_QR,
            caption=caption,
            reply_markup=reply_markup
        )
    else:
        await app.send_photo(
            target,
            photo=PAYMENT_QR,
            caption=caption,
            reply_markup=reply_markup
        )

# -------------------------
# Command: /start
# -------------------------
@app.on_message(filters.command("start") & filters.private)
async def cmd_start(_, m: Message):
    user = m.from_user
    if not user:
        return

    # persist or update user
    db.add_or_update_user(user.id, getattr(user, "username", None), getattr(user, "first_name", None), getattr(user, "last_name", None))

    caption = (
        "👋 *Welcome!*\n\n"
        "💖 *Permanent Membership* — *₹499* (limited offer)\n\n"
        "✅ Direct videos uploads\n"
        "✅ Daily new updates\n"
        "✅ 10,000+ videos already\n\n"
        "⚠️ Check the demo channel before buying.\n\n"
        "Tap below to pay and get premium."
    )
    await m.reply_text(caption, reply_markup=main_buy_keyboard())

# -------------------------
# Command: /help
# -------------------------
@app.on_message(filters.command("help") & filters.private)
async def cmd_help(_, m: Message):
    text = (
        "Commands:\n"
        "/start - start & buy\n"
        "/support - contact support\n\n"
        "Admin commands (only admin can use):\n"
        "/users - total users\n"
        "/listp - show premium buyers\n"
        "/broadcast - reply to message to broadcast\n"
    )
    await m.reply_text(text)

# -------------------------
# Command: /support
# -------------------------
@app.on_message(filters.command("support") & filters.private)
async def cmd_support(_, m: Message):
    await m.reply_text(
        "If you need help, contact the admin using the button below.",
        reply_markup=support_keyboard
    )

# -------------------------
# Admin: /users
# -------------------------
@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def cmd_users(_, m: Message):
    user_ids = db.get_all_user_ids()
    await m.reply_text(f"👥 Total users recorded: {len(user_ids)}")

# -------------------------
# Admin: /listp -> premium buyers
# -------------------------
@app.on_message(filters.command("listp") & filters.user(ADMIN_ID))
async def cmd_listp(_, m: Message):
    data = db.get_premium_by_date()
    if not data:
        return await m.reply_text("📊 No premium purchases yet.")

    today = today_date_str()
    today_count = db.get_premium_count_today()

    lines = [f"📊 *Premium Buyers Report*", f"🗓 Today ({today}) → *{today_count}* user(s)\n"]
    # sort dates descending
    for date in sorted(data.keys(), reverse=True):
        buyers = data[date]
        lines.append(f"📅 {date} → {len(buyers)} user(s)")
        for b in buyers:
            uid = b["user_id"]
            uname = b["username"] or "N/A"
            fname = b["first_name"] or "N/A"
            approved_at = b["approved_at"]
            lines.append(f"   └ {fname} ({uname}) — ID: {uid} — {approved_at}")
        lines.append("")  # blank line

    await m.reply_text("\n".join(lines))

# -------------------------
# Admin: /broadcast (reply to a message)
# -------------------------
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def cmd_broadcast(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("Reply to a message you want to broadcast to all users.")

    user_ids = db.get_all_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await app.copy_message(uid, m.chat.id, m.reply_to_message.message_id)
            sent += 1
        except Exception:
            continue

    await m.reply_text(f"✅ Broadcast sent to {sent} users.")

# -------------------------
# Payment flow: send QR (callback)
# -------------------------
@app.on_callback_query(filters.regex(r"^pay_now$"))
async def cb_pay_now(_, cb: CallbackQuery):
    await cb.answer()
    caption = (
        "💎 *PAY ₹499 TO GET PREMIUM ACCESS*\n\n"
        f"📷 Scan QR or pay via UPI:\n`{UPI_ID}`\n\n"
        "⚡ After payment, tap *Payment Done* and send the screenshot here (do not forward)."
    )
    # Always send ONLY the QR image + caption (no fallback text)
    await send_payment_qr_only(cb.message, caption, reply_markup=qr_payment_keyboard())

# -------------------------
# Optional: retry QR resend (if you want a retry button)
# -------------------------
@app.on_callback_query(filters.regex(r"^retry_payment$"))
async def cb_retry_payment(_, cb: CallbackQuery):
    await cb.answer()
    caption = (
        "⚠️ *Payment not detected.*\n\n"
        f"Please try again. UPI: `{UPI_ID}`\n\n"
        "Scan the QR below and then tap *Payment Done*."
    )
    await send_payment_qr_only(cb.message, caption, reply_markup=qr_payment_keyboard())

# -------------------------
# Payment Done: user clicked after paying
# - mark pending in DB and ask user to send screenshot (if not already sent)
# - we will still ask for screenshot but will not spam double messages
# -------------------------
@app.on_callback_query(filters.regex(r"^payment_done$"))
async def cb_payment_done(_, cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    # if already premium, inform and stop
    if db.is_premium(uid):
        return await cb.message.reply_text("✅ You already have premium access. Thank you!")

    # mark pending (if not already)
    db.mark_pending(uid, file_id="")  # file_id blank until user uploads photo

    # instruct user to send screenshot: we use reply_text (single message)
    await cb.message.reply_text(
        "📤 Please send a screenshot of your payment receipt as a photo (do not forward). "
        "It will be sent to admin for verification.",
        reply_markup=support_keyboard
    )

# -------------------------
# Photo handler: when user sends screenshot photo in private chat
# - only accept if user is marked pending
# - reject forwarded media
# - send the screenshot (file_id) + admin approve/reject buttons to ADMIN_ID
# -------------------------
@app.on_message(filters.photo & filters.private)
async def on_photo(_, m: Message):
    user = m.from_user
    if not user:
        return

    pending = db.get_pending(user.id)
    # If not pending, ignore silently
    if not pending:
        return

    # ignore forwarded photos
    if m.forward_date:
        return await m.reply_text("Please do not forward screenshots. Send the original screenshot.")

    # Get file_id (best quality photo)
    file_id = m.photo.file_id

    # store file_id in pending db
    db.set_pending_file(user.id, file_id)

    # Build caption for admin with user details and time
    caption = (
        f"🧾 *Payment Screenshot Received*\n\n"
        f"👤 Name: {user.first_name or 'N/A'}\n"
        f"🔗 Username: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user.id}\n"
        f"⏰ Time: {now_str()}\n\n"
        "Use the buttons below to Approve or Reject."
    )

    try:
        # send to admin with approve/reject buttons targeted to this user id
        await app.send_photo(
            ADMIN_ID,
            photo=file_id,
            caption=caption,
            reply_markup=admin_verify_keyboard(user.id)
        )
    except Exception as e:
        logger.exception("Failed to send screenshot to admin: %s", e)
        # fallback: send as message (still include buttons)
        try:
            await app.send_message(ADMIN_ID, caption, reply_markup=admin_verify_keyboard(user.id))
        except Exception:
            logger.exception("Also failed to send admin message.")

    # inform user that admin will check (single message)
    await m.reply_text("📸 Your screenshot has been sent to admin for verification. Please wait.")

# -------------------------
# Admin approves
# - callback pattern: approve_<user_id>
# -------------------------
@app.on_callback_query(filters.regex(r"^approve_(\d+)$") & filters.user(ADMIN_ID))
async def cb_approve(_, cb: CallbackQuery):
    await cb.answer("Approved ✅")
    data = cb.data or ""
    try:
        uid = int(data.split("_", 1)[1])
    except Exception:
        return await cb.message.reply_text("Invalid approval callback data.")

    # If already premium, remove admin buttons and inform
    if db.is_premium(uid):
        try:
            await cb.message.edit_reply_markup(None)
        except Exception:
            pass
        return await cb.message.reply_text(f"User {uid} is already a premium buyer.")

    # add to premium buyers
    # try fetching user info in DB; if not present, use placeholders
    user_row = db.get_user(uid)
    uname = user_row["username"] if user_row else ""
    fname = user_row["first_name"] if user_row else ""

    db.add_premium_buyer(uid, uname, fname, ADMIN_ID)
    db.remove_pending(uid)

    # Notify user
    try:
        await app.send_message(
            uid,
            "🎉 Congratulations! Your premium access has been activated.\n\n"
            "Join the premium channel below.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Premium Channel", url="https://t.me/Alex_clb")]]),
        )
    except Exception:
        logger.exception("Failed to send activation message to user %s", uid)

    # Remove approve/reject buttons from the admin message to prevent re-press
    try:
        await cb.message.edit_reply_markup(None)
    except Exception:
        pass

    # Confirm to admin
    await cb.message.reply_text(f"User {uid} approved and added to premium buyers.")

# -------------------------
# Admin rejects
# - callback pattern: reject_<user_id>
# -------------------------
@app.on_callback_query(filters.regex(r"^reject_(\d+)$") & filters.user(ADMIN_ID))
async def cb_reject(_, cb: CallbackQuery):
    await cb.answer("Rejected ❌")
    data = cb.data or ""
    try:
        uid = int(data.split("_", 1)[1])
    except Exception:
        return await cb.message.reply_text("Invalid reject callback data.")

    # remove pending (if exists)
    db.remove_pending(uid)

    # notify user
    try:
        await app.send_message(
            uid,
            "❌ Your payment could not be verified. Please contact support or try again.",
            reply_markup=support_keyboard
        )
    except Exception:
        logger.exception("Failed to notify user about rejection: %s", uid)

    # Remove buttons from admin message
    try:
        await cb.message.edit_reply_markup(None)
    except Exception:
        pass

    await cb.message.reply_text(f"User {uid} rejected and notified.")

# -------------------------
# Safety: block non-admins from calling approve/reject
# (This will silently ignore non-admin presses, but we already used filters.user for admin callbacks.)
# -------------------------
# (No additional code required; filters.user(ADMIN_ID) guards admin callbacks.)

# -------------------------
# Fallback: gracefully handle errors
# -------------------------
@app.on_message(filters.private)
async def catch_all_private(_, m: Message):
    """
    Catch-all in private chats to update user info and help guide.
    Avoids interfering with photo handler because filters.photo is processed earlier.
    """
    user = m.from_user
    if user:
        db.add_or_update_user(user.id, getattr(user, "username", None), getattr(user, "first_name", None), getattr(user, "last_name", None))

    # If the message is a command, other handlers will handle; this is just a gentle nudge
    if m.text and m.text.startswith("/"):
        return  # don't reply to commands here

    # For other messages, do not spam. Offer support only when user asks.
    # Keep this handler silent.

# -------------------------
# Start bot
# -------------------------
if __name__ == "__main__":
    logger.info("Starting Premium Bot...")
    try:
        app.run()
    except Exception as exc:
        logger.exception("Bot crashed: %s", exc)
