# Numbot.py - Python 3.11 Compatible
import requests
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8685653597:AAHscWTwMRCY93q9qQlAM3EKGTE27Sx36Tc"
API_URL = "https://sher-osint-india-num-info.vercel.app/api?number={}"

# Database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        credits INTEGER DEFAULT 10
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

def add_user(user_id, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username or "User"))
    conn.commit()
    conn.close()

def update_credits(user_id, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    user_data = get_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search", callback_data="search")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")]
    ]
    
    await update.message.reply_text(
        f"✅ Welcome {user.first_name}!\n\n💀 NUM INFO BOT\n💳 Credits: {user_data[2] if user_data else 10}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data or user_data[2] <= 0:
        await update.message.reply_text("❌ Insufficient credits!")
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❌ /search 9876543210")
        return
    
    update_credits(user_id, -1)
    
    try:
        response = requests.get(API_URL.format(query), timeout=10)
        data = response.json()
    except:
        await update.message.reply_text("⚠️ API Error")
        update_credits(user_id, 1)
        return
    
    if not data.get("success"):
        await update.message.reply_text("❌ Number not found!")
        update_credits(user_id, 1)
        return
    
    details = data.get("number_detail", {})
    msg = f"📞 Number: {query}\n👤 Name: {details.get('name', 'N/A')}\n📡 Operator: {details.get('operator', 'N/A')}\n💳 Credits Left: {user_data[2] - 1}"
    
    await update.message.reply_text(msg)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.edit_message_text("Send: /search 9876543210")
    elif query.data == "profile":
        user_data = get_user(query.from_user.id)
        if user_data:
            await query.edit_message_text(f"👤 Profile\nCredits: {user_data[2]}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit() and len(text) == 10:
        context.args = [text]
        await search_command(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🔥 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()    conn.commit()
    conn.close()

def update_credits(user_id, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    user_data = get_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search", callback_data="search")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")]
    ]
    
    await update.message.reply_text(
        f"✅ Welcome {user.first_name}!\n\n💀 NUM INFO BOT\n💳 Credits: {user_data[2] if user_data else 10}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data or user_data[2] <= 0:
        await update.message.reply_text("❌ Insufficient credits!")
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❌ /search 9876543210")
        return
    
    update_credits(user_id, -1)
    
    try:
        response = requests.get(API_URL.format(query), timeout=10)
        data = response.json()
    except:
        await update.message.reply_text("⚠️ API Error")
        update_credits(user_id, 1)
        return
    
    if not data.get("success"):
        await update.message.reply_text("❌ Number not found!")
        update_credits(user_id, 1)
        return
    
    details = data.get("number_detail", {})
    msg = f"📞 Number: {query}\n👤 Name: {details.get('name', 'N/A')}\n📡 Operator: {details.get('operator', 'N/A')}\n💳 Credits Left: {user_data[2] - 1}"
    
    await update.message.reply_text(msg)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.edit_message_text("Send: /search 9876543210")
    elif query.data == "profile":
        user_data = get_user(query.from_user.id)
        if user_data:
            await query.edit_message_text(f"👤 Profile\nCredits: {user_data[2]}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit() and len(text) == 10:
        context.args = [text]
        await search_command(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🔥 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
