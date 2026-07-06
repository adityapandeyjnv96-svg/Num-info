# Numbot.py - Render Version
import requests
import sqlite3
import datetime
import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# === CONFIG ===
BOT_TOKEN = "8685653597:AAHscWTwMRCY93q9qQlAM3EKGTE27Sx36Tc"
API_URL = "https://sher-osint-india-num-info.vercel.app/api?number={}"
OWNER_IDS = [5546171977, 8781746926]

# === DATABASE ===
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        verified INTEGER DEFAULT 1,
        credits INTEGER DEFAULT 10,
        total_searches INTEGER DEFAULT 0,
        join_date TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
              (user_id, username or "NoUsername", first_name or "User", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def update_credits(user_id, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def is_owner(user_id):
    return user_id in OWNER_IDS

def escape(text):
    if not text:
        return "N/A"
    return str(text).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')

# === COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    user_data = get_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search", callback_data="search")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    
    await update.message.reply_text(
        f"✅ Welcome {user.first_name}!\n\n"
        f"💀 NUM INFO BOT\n"
        f"💳 Credits: {user_data[4] if user_data else 10}\n\n"
        f"Select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data[4] <= 0:
        await update.message.reply_text("❌ Insufficient credits!")
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❌ Send number: /search 9876543210")
        return
    
    update_credits(user_id, -1)
    
    try:
        response = requests.get(API_URL.format(query), timeout=30)
        data = response.json()
    except:
        await update.message.reply_text("⚠️ API Error. Try again later.")
        update_credits(user_id, 1)
        return
    
    if not data.get("success"):
        await update.message.reply_text("❌ Number not found!")
        update_credits(user_id, 1)
        return
    
    details = data.get("number_detail", {})
    msg = (
        f"📞 Number: {query}\n"
        f"👤 Name: {escape(details.get('name', 'N/A'))}\n"
        f"📧 Email: {escape(details.get('email', 'N/A'))}\n"
        f"📡 Operator: {escape(details.get('operator', 'N/A'))}\n"
        f"📍 Address: {escape(details.get('full_address', 'N/A'))}\n"
        f"🏙️ City: {escape(details.get('village_city', 'N/A'))}\n"
        f"💳 Credits Left: {user_data[4] - 1}"
    )
    
    await update.message.reply_text(msg)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "search":
        await query.edit_message_text("Send number: /search 9876543210")
    elif data == "profile":
        user_data = get_user(query.from_user.id)
        await query.edit_message_text(
            f"👤 Profile\n"
            f"ID: {user_data[0]}\n"
            f"Name: {user_data[2]}\n"
            f"Credits: {user_data[4]}\n"
            f"Searches: {user_data[5]}"
        )
    elif data == "support":
        await query.edit_message_text("📞 Support: @Mohtdader90")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit() and len(text) == 10:
        context.args = [text]
        await search_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("🔥 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()    c.execute('''CREATE TABLE IF NOT EXISTS pending_users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        request_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        number TEXT,
        search_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('verification_required', 'true')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_searches', '0')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('offer_message', '')")
    conn.commit()
    conn.close()

init_db()

# === SETTINGS FUNCTIONS ===
def get_setting(key):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_setting(key, value):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

# === DATABASE FUNCTIONS ===
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
              (user_id, username or "NoUsername", first_name or "User", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_credits(user_id, credits):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (credits, user_id))
    conn.commit()
    conn.close()

def add_pending_user(user_id, username, first_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO pending_users (user_id, username, first_name, request_date) VALUES (?, ?, ?, ?)",
              (user_id, username or "NoUsername", first_name or "User", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_pending_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pending_users")
    users = c.fetchall()
    conn.close()
    return users

def verify_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET verified = 1 WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM pending_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def reject_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM pending_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_search_history(user_id, number):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO search_history (user_id, number, search_date) VALUES (?, ?, ?)",
              (user_id, number, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.execute("UPDATE users SET total_searches = total_searches + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_all_verified_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE verified = 1")
    users = c.fetchall()
    conn.close()
    return users

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

def is_owner(user_id):
    return user_id in OWNER_IDS

# === COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    user_data = get_user(user.id)
    verification_required = get_setting('verification_required') == 'true'
    free_searches = int(get_setting('free_searches') or 0)
    offer_message = get_setting('offer_message') or ""
    
    is_verified = user_data and user_data[3] == 1
    can_use = is_verified or not verification_required
    
    if can_use:
        keyboard = [
            [InlineKeyboardButton("🔍 Search Number", callback_data="search")],
            [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
            [InlineKeyboardButton("📞 Support", callback_data="support")],
            [InlineKeyboardButton("👑 Owner", callback_data="owner")]
        ]
        if is_owner(user.id):
            keyboard.append([InlineKeyboardButton("⚙️ Owner Panel", callback_data="owner_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = f"✅ Welcome {user.first_name}!\n\n"
        msg += f"💀 NUM INFO BOT 💀\n"
        msg += f"🔹 Credits: {user_data[4] if user_data else 0}\n"
        msg += f"🔹 Total Searches: {user_data[5] if user_data else 0}\n"
        
        if free_searches > 0:
            msg += f"🎉 Free Searches Available: {free_searches}\n"
        
        if offer_message:
            msg += f"\n📢 {offer_message}\n"
        
        msg += f"\nSelect an option below:"
        
        await update.message.reply_text(msg, reply_markup=reply_markup)
    else:
        add_pending_user(user.id, user.username, user.first_name)
        keyboard = [[InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⏳ Hello {user.first_name}!\n\n"
            f"Your account is pending verification.\n"
            f"Please wait for owner to verify you.\n"
            f"Or contact support: {SUPPORT_USERNAME}\n\n"
            f"🔹 Developer: {DEVELOPER_USERNAME}",
            reply_markup=reply_markup
        )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    verification_required = get_setting('verification_required') == 'true'
    free_searches = int(get_setting('free_searches') or 0)
    
    is_verified = user_data and user_data[3] == 1
    can_use = is_verified or not verification_required
    
    if not can_use:
        await update.message.reply_text("❌ You are not verified! Use /start and wait for approval.")
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text(
            "❌ Please provide a number!\n"
            "Example: /search 9876543210"
        )
        return
    
    current_credits = user_data[4] if user_data else 0
    if current_credits <= 0:
        await update.message.reply_text("❌ Insufficient credits! Contact owner to add credits.")
        return
    
    update_user_credits(user_id, -1)
    
    try:
        response = requests.get(API_URL.format(query), timeout=10)
        data = response.json()
    except Exception as e:
        await update.message.reply_text(f"⚠️ API Error: {str(e)}")
        update_user_credits(user_id, 1)
        return
    
    if not data.get("success"):
        await update.message.reply_text("❌ Number not found!")
        update_user_credits(user_id, 1)
        return
    
    add_search_history(user_id, query)
    
    details = data.get("number_detail", {})
    
    number = escape_markdown(data.get('number', 'N/A'))
    name = escape_markdown(details.get('name', 'N/A'))
    email = escape_markdown(details.get('email', 'N/A'))
    father = escape_markdown(details.get('father_name', 'N/A'))
    operator = escape_markdown(details.get('operator', 'N/A'))
    circle = escape_markdown(details.get('circle', 'N/A'))
    address = escape_markdown(details.get('full_address', 'N/A'))
    city = escape_markdown(details.get('village_city', 'N/A'))
    pincode = escape_markdown(details.get('pincode', 'N/A'))
    state = escape_markdown(details.get('state', 'N/A'))
    
    new_credits = current_credits - 1
    msg = (
        f"📞 Number: {number}\n"
        f"👤 Name: {name}\n"
        f"📧 Email: {email}\n"
        f"👨‍👦 Father: {father}\n"
        f"📡 Operator: {operator}\n"
        f"🌐 Circle: {circle}\n"
        f"📍 Address: {address}\n"
        f"🏙️ City: {city}\n"
        f"📮 Pincode: {pincode}\n"
        f"🗺️ State: {state}\n"
        f"\n💳 Credits Left: {new_credits}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search Again", callback_data="search")],
        [InlineKeyboardButton("👑 Owner", callback_data="owner")]
    ]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ This command is only for the owner!")
        return
    
    pending = get_pending_users()
    verification_required = get_setting('verification_required') == 'true'
    free_searches = int(get_setting('free_searches') or 0)
    offer_message = get_setting('offer_message') or "No active offer"
    
    keyboard = []
    
    if verification_required and pending:
        keyboard.append([InlineKeyboardButton("📋 Pending Users", callback_data="pending_list")])
    
    status_text = "✅ ON" if verification_required else "❌ OFF"
    keyboard.append([InlineKeyboardButton(f"🔐 Verification: {status_text}", callback_data="toggle_verification")])
    
    keyboard.extend([
        [InlineKeyboardButton("👥 All Users", callback_data="all_users")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("➕ Add Credits", callback_data="add_credits")],
        [InlineKeyboardButton("🎉 Free Searches", callback_data="free_searches")],
        [InlineKeyboardButton("📢 Set Offer", callback_data="set_offer")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ])
    
    msg = (
        f"👑 Owner Panel\n\n"
        f"📋 Pending Users: {len(pending) if verification_required else 'N/A (Disabled)'}\n"
        f"🔐 Verification: {'ON' if verification_required else 'OFF'}\n"
        f"🎉 Free Searches: {free_searches}\n"
        f"📢 Offer: {offer_message[:30]}...\n\n"
        f"Select an option:"
    )
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# === CALLBACK HANDLERS ===

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if data == "search":
        await query.edit_message_text(
            "🔍 Search Number\n\n"
            "Send a number to search:\n"
            "Example: 9876543210"
        )
        context.user_data['awaiting_number'] = True
    
    elif data == "profile":
        user_data = get_user(user_id)
        if user_data:
            username = user_data[1] if user_data[1] and user_data[1] != 'NoUsername' else 'N/A'
            msg = (
                f"👤 Your Profile\n\n"
                f"🆔 ID: {user_data[0]}\n"
                f"👤 Name: {user_data[2]}\n"
                f"🔹 Username: {username}\n"
                f"✅ Verified: {'✅' if user_data[3] == 1 else '❌'}\n"
                f"💳 Credits: {user_data[4]}\n"
                f"🔍 Total Searches: {user_data[5]}\n"
                f"📅 Joined: {user_data[6]}"
            )
            await query.edit_message_text(msg)
    
    elif data == "support":
        keyboard = [
            [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.edit_message_text(
            f"📞 Support\n\n"
            f"Contact: {SUPPORT_USERNAME}\n"
            f"Developer: {DEVELOPER_USERNAME}\n\n"
            f"Feel free to reach out for help!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "owner":
        keyboard = [
            [InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.edit_message_text(
            f"👑 Owner Info\n\n"
            f"Owner: {SUPPORT_USERNAME}\n"
            f"Developer: {DEVELOPER_USERNAME}\n\n"
            f"Bot created by {DEVELOPER_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "owner_panel":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        await owner_panel(update, context)
    
    elif data == "pending_list":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        pending = get_pending_users()
        if not pending:
            await query.edit_message_text("✅ No pending users!")
            return
        
        await query.edit_message_text("📋 Pending Users List:\n\nCheck below:")
        for user in pending:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user[0]}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user[0]}")
                ]
            ]
            await query.message.reply_text(
                f"🆔 User ID: {user[0]}\n"
                f"👤 Name: {user[2]}\n"
                f"🔹 Username: @{user[1] if user[1] != 'NoUsername' else 'N/A'}\n"
                f"📅 Requested: {user[3]}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif data == "toggle_verification":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        current = get_setting('verification_required') == 'true'
        new_value = 'false' if current else 'true'
        update_setting('verification_required', new_value)
        
        status = "OFF" if new_value == 'false' else "ON"
        await query.edit_message_text(f"✅ Verification system turned {status}!\n\n"
                                       f"Users can now {'use the bot freely' if new_value == 'false' else 'need approval'}.")
        
        if new_value == 'false':
            users = get_all_users()
            for user in users:
                try:
                    await context.bot.send_message(
                        user[0],
                        "🎉 Good News!\n\n"
                        "Verification is now OFF.\n"
                        "You can use the bot freely now!\n"
                        "Use /start to begin."
                    )
                except:
                    pass
    
    elif data == "free_searches":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        await query.edit_message_text(
            "🎉 Free Searches\n\n"
            "Send command:\n"
            "/freesearches AMOUNT\n\n"
            "Example: /freesearches 5\n"
            "This gives 5 free searches to all users."
        )
    
    elif data == "set_offer":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        await query.edit_message_text(
            "📢 Set Offer\n\n"
            "Send command:\n"
            "/offer YOUR_MESSAGE\n\n"
            "Example: /offer 50% off on credits!\n"
            "This will show to all users."
        )
    
    elif data == "add_credits":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        await query.edit_message_text(
            "➕ Add Credits\n\n"
            "Send: /addcredits USER_ID AMOUNT\n"
            "Example: /addcredits 123456789 50"
        )
    
    elif data == "broadcast":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        await query.edit_message_text(
            "📢 Broadcast\n\n"
            "Send: /broadcast MESSAGE\n"
            "Example: /broadcast Hello everyone!"
        )
    
    elif data == "all_users":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        users = get_all_users()
        verified = sum(1 for u in users if u[3] == 1)
        pending = get_pending_users()
        
        await query.edit_message_text(
            f"👥 All Users\n\n"
            f"Total Users: {len(users)}\n"
            f"Verified: {verified}\n"
            f"Pending: {len(pending)}\n"
            f"Unverified: {len(users) - verified - len(pending)}"
        )
    
    elif data == "stats":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT SUM(total_searches) FROM users")
        total_searches = c.fetchone()[0] or 0
        c.execute("SELECT SUM(credits) FROM users")
        total_credits = c.fetchone()[0] or 0
        conn.close()
        
        users = get_all_users()
        
        await query.edit_message_text(
            f"📊 Bot Stats\n\n"
            f"👥 Total Users: {len(users)}\n"
            f"🔍 Total Searches: {total_searches}\n"
            f"💳 Total Credits: {total_credits}\n"
            f"🎉 Free Searches: {get_setting('free_searches')}\n"
            f"🔐 Verification: {'ON' if get_setting('verification_required') == 'true' else 'OFF'}"
        )
    
    elif data.startswith("approve_"):
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        target_id = int(data.split("_")[1])
        verify_user(target_id)
        update_user_credits(target_id, 10)
        await query.edit_message_text(f"✅ User {target_id} verified and got 10 credits!")
        
        try:
            await context.bot.send_message(
                target_id,
                "🎉 Congratulations!\n\n"
                "Your account has been verified!\n"
                "You received 10 free credits.\n"
                "Use /start to begin."
            )
        except:
            pass
    
    elif data.startswith("reject_"):
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        target_id = int(data.split("_")[1])
        reject_user(target_id)
        await query.edit_message_text(f"❌ User {target_id} rejected!")
        
        try:
            await context.bot.send_message(
                target_id,
                "❌ Sorry!\n\n"
                "Your verification request has been rejected.\n"
                "Contact support for more info."
            )
        except:
            pass
    
    elif data == "back":
        await start(update, context)

# === OWNER COMMANDS ===

async def add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access denied!")
        return
    
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("❌ Usage: /addcredits USER_ID AMOUNT")
        return
    
    try:
        target_id = int(args[0])
        amount = int(args[1])
        update_user_credits(target_id, amount)
        await update.message.reply_text(f"✅ Added {amount} credits to user {target_id}!")
    except:
        await update.message.reply_text("❌ Invalid input!")

async def free_searches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access denied!")
        return
    
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("❌ Usage: /freesearches AMOUNT\nExample: /freesearches 5")
        return
    
    try:
        amount = int(args[0])
        update_setting('free_searches', str(amount))
        
        users = get_all_verified_users()
        for user in users:
            update_user_credits(user[0], amount)
        
        await update.message.reply_text(f"✅ Added {amount} free searches to all users!")
        
        for user in users:
            try:
                await context.bot.send_message(
                    user[0],
                    f"🎉 Free Searches!\n\n"
                    f"You received {amount} free credits!\n"
                    f"Use /start to check your balance."
                )
            except:
                pass
    except:
        await update.message.reply_text("❌ Invalid amount!")

async def set_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access denied!")
        return
    
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("❌ Usage: /offer MESSAGE\nExample: /offer 50% off on credits!")
        return
    
    update_setting('offer_message', message)
    await update.message.reply_text(f"✅ Offer set:\n\n📢 {message}")
    
    users = get_all_verified_users()
    for user in users:
        try:
            await context.bot.send_message(
                user[0],
                f"📢 New Offer!\n\n{message}"
            )
        except:
            pass

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access denied!")
        return
    
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("❌ Usage: /broadcast MESSAGE")
        return
    
    users = get_all_verified_users()
    success = 0
    
    for user in users:
        try:
            await context.bot.send_message(user[0], f"📢 Broadcast\n\n{message}")
            success += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Broadcast sent to {success} users!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if context.user_data.get('awaiting_number'):
        if not text.isdigit() or len(text) < 10:
            await update.message.reply_text("❌ Invalid number! Send a valid 10-digit number.")
            return
        
        context.args = [text]
        await search_command(update, context)
        context.user_data['awaiting_number'] = False

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raise context.error
    except Exception as e:
        if update and update.effective_user:
            await context.bot.send_message(
                update.effective_user.id,
                f"⚠️ An error occurred: {str(e)[:100]}"
            )
        print(f"Error: {e}")

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("owner", owner_panel))
    app.add_handler(CommandHandler("addcredits", add_credits))
    app.add_handler(CommandHandler("freesearches", free_searches))
    app.add_handler(CommandHandler("offer", set_offer))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("🔥 Advanced Bot is running...")
    print(f"👑 Owners: {OWNER_IDS}")
    app.run_polling()

if __name__ == "__main__":
    main()
