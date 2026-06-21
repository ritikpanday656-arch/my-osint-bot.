import telebot
import requests
import random
import string
import time
import sqlite3
import os
from threading import Thread
import urllib3

# Security bypass configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session_adapter = requests.adapters.HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=3)

# 1. CONFIGURATION (Naya Token Added)
BOT_TOKEN = '8625741276:AAHS4SY1L8hY-JO1Ka89t1X1edVelMS6y6I'  
ADMIN_CHAT_ID = 8185875154  # Master Admin Access ID

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=6)

API_URL = "https://v2.hi2.in/api/v1/"
AVAILABLE_DOMAINS = ["hi2.in"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://hi2.in",
    "Referer": "https://hi2.in/"
}

# 2. DATABASE SETUP
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, phone TEXT DEFAULT 'None')")
    cursor.execute("CREATE TABLE IF NOT EXISTS emails (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, domain TEXT, email_id TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS custom_domains (user_id INTEGER, domain_name TEXT PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS seen_messages (email_id TEXT, msg_id INTEGER, PRIMARY KEY (email_id, msg_id))")
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect('bot_database.db')

def register_user(user_id, username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id == ADMIN_CHAT_ID

# ==================== MASTER ADMIN PANEL COMMANDS ====================

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ You are not authorized to use admin commands.")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]
    conn.close()
    
    panel_txt = (
        "⚙️ **MASTER ADMIN CONTROL PANEL** ⚙️\n\n"
        f"📊 **Total Active Users:** {total_users}\n"
        f"✉️ **Total Registered Fake Mail IDs:** {total_emails}\n"
        "🌐 **Server Engine Matrix:** Online [Render Cloud Stable]\n\n"
        "🛠️ **Commands Available:**\n"
        "• `/broadcast [Your Message]` - Send notification to all users\n"
        "• `/stats` - Check database health status indicators"
    )
    bot.reply_to(message, panel_txt, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if not is_admin(message.chat.id):
        return
        
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Usage: `/broadcast Hello Users`")
        return
        
    broadcast_msg = args[1]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users_list = cursor.fetchall()
    conn.close()
    
    success_count = 0
    bot.reply_to(message, f"📢 Starting broadcast to {len(users_list)} users...")
    
    for row in users_list:
        try:
            bot.send_message(row[0], f"📢 **ANNOUNCEMENT FROM ADMIN:**\n\n{broadcast_msg}", parse_mode="Markdown")
            success_count += 1
            time.sleep(0.1)
        except:
            pass
            
    bot.send_message(message.chat.id, f"✅ Broadcast Complete! Sent to {success_count}/{len(users_list)} users.")

@bot.message_handler(commands=['stats'])
def admin_stats(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "📊 **SYSTEM LOG STATUS:**\n\n• Connection: Render Active Node\n• Rate-Limits: Clean\n• Active Threads: 6")

# ==================== GENERAL USER BOT COMMANDS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uname = message.from_user.username if message.from_user.username else "nousername"
    register_user(message.chat.id, uname.lower())
    
    welcome_txt = (
        "✨ **HELLO WELCOME TO SP OSINT BOT** ✨\n"
        "-----------------------------------------\n"
        "📢 **ADD ME ON YOUR GROUP AND SHARE AND SUPPORT US**\n\n"
        "🤖 **Available Operations Menu:**\n"
        "• `/generate` - Get a new random temporary email ID\n"
        "• `/id` - Check all your currently active email profiles\n"
        "• `/set` - Create custom premium mail handle formats\n"
        "• `/phone` - Setup/Update your user recovery register link\n"
        "• `/domain` - Manage proxy and linked system domains\n"
        "• `/transfer` - Send mail identity data to another group user\n\n"
        "⚡ *Type any command or text below to execute operations immediately.*"
    )
    bot.reply_to(message, welcome_txt, parse_mode="Markdown")

@bot.message_handler(commands=['generate'])
def generate_cmd(message):
    user_id = message.chat.id
    uname = message.from_user.username if message.from_user.username else "nousername"
    register_user(user_id, uname.lower())
    
    u = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    d = "hi2.in"
    full_mail = f"{u}@{d}"
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO emails (user_id, username, domain, email_id) VALUES (?, ?, ?, ?)", (user_id, u, d, full_mail))
        conn.commit()
        bot.reply_to(message, f"Your new fake mail id is {full_mail}\nsend /id to see the full list.")
    except Exception as e:
        bot.reply_to(message, "⚠️ Error creating temporary mailbox.")
    conn.close()

@bot.message_handler(commands=['id'])
def id_cmd(message):
    user_id = message.chat.id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email_id FROM emails WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        bot.send_message(user_id, "ℹ️ You don't have any active fake mail IDs.")
        conn.close()
        return
    response_text = "here are the list of fake mail ids you have\n"
    for index, row in enumerate(rows, start=1):
        db_id, email = row
        response_text += f"{index}. {email} | /delete_{db_id}\n"
    conn.close()
    bot.send_message(user_id, response_text, disable_web_page_preview=True)

@bot.message_handler(commands=['set'])
def set_cmd(message):
    bot.reply_to(message, "ℹ️ To setup a custom username name layout, simply type the clean text directly into the chat box field.")

@bot.message_handler(commands=['phone'])
def phone_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "ℹ️ Use syntax: `/phone +91XXXXXXXXXX` to add/update your recovery number.")
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (args[1], message.chat.id))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ Recovery phone number updated successfully.")

@bot.message_handler(commands=['domain'])
def domain_cmd(message):
    domain_text = (
        f"**SP X DEALER**\n/domain\n\n"
        "**Your domains list**\n\n"
        "If you want a new domain buy from here https://www.namesilo.com/register.php?rid=7312823ug\n"
        "If you already own a domain and want to add here send `/adddomain
  
