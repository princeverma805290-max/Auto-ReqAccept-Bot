import os
import asyncio
import datetime
import time
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from motor.motor_asyncio import AsyncIOMotorClient

# --- RENDER PORT BINDING ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=1234)

threading.Thread(target=run_web).start()

# --- CONFIGURATION ---
API_ID = 33568744
API_HASH = "362b41958aa6a949dbe789bbf82d01e8"
BOT_TOKEN = "8267135540:AAESIn5KuPL0rPl3vVTWsdm6b3axEGhCeao"
DB_URL = "mongodb+srv://princeverma:Pkgamingff347@tp-auto-aprove-bot.8hc3wp3.mongodb.net/?appName=TP-APROVE-BOT"
ADMINS = 8241838848

# --- DATABASE SETUP ---
Dbclient = AsyncIOMotorClient(DB_URL)
Cluster = Dbclient['Cluster0']
Data = Cluster['users']

# --- BOT CLIENT ---
Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
    button = [[
        InlineKeyboardButton('Updates', url='https://t.me/TP_Bot_Updates'),
        InlineKeyboardButton('Support', url='https://t.me/TP_Chats_02')
    ]]
    
    START_TEXT = "Hai {}\n\nI am Auto Request Accept Bot. Add Me In Your Channel To Use"
    await m.reply_text(
        text=START_TEXT.format(m.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(button)
    )

@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
    await c.approve_chat_join_request(chat_id, user_id)
    try:
        ACCEPTED_TEXT = "Hey {user}\n\nYour Request For {chat} Is Accepted ✅"
        await c.send_message(user_id, ACCEPTED_TEXT.format(user=m.from_user.mention, chat=m.chat.title))
    except Exception as e:
        print(e)

Bot.run()



