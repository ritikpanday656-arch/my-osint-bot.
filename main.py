
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

# 1. CONFIGURATION (Naya Token Automatically Added)
BOT_TOKEN = '8988252782:AAHq2g1Jnz2n52zhDXZRXscS-hmsdfc6m7M'  
ADMIN_CHAT_ID = 8185875154  # Aapki Admin Telegram ID

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS
        
