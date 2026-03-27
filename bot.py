import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from motor.motor_asyncio import AsyncIOMotorClient

# --- RENDER PORT SETUP ---
app = Flask(__name__)
@app.route('/')
def hello(): return "Bot is Running!"
def run_web(): app.run(host='0.0.0.0', port=1234)
threading.Thread(target=run_web).start()

# --- CONFIGURATION ---
API_ID = 33568744
API_HASH = "362b41958aa6a949dbe789bbf82d01e8"
BOT_TOKEN = "8267135540:AAESIn5KuPL0rPl3vVTWsdm6b3axEGhCeao"
DB_URL = "mongodb+srv://princeverma:Pkgamingff347@tp-auto-aprove-bot.8hc3wp3.mongodb.net/?appName=TP-APROVE-BOT"
ADMINS = 8241838848
BACKUP_CHANNEL = "https://t.me/TP_Bot_Updates"

# --- DATABASE ---
Dbclient = AsyncIOMotorClient(DB_URL)
Data = Dbclient['Cluster0']['users']
LinkData = Dbclient['Cluster0']['links']

Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. SET LINK COMMAND
@Bot.on_message(filters.command("setlink") & filters.user(ADMINS))
async def set_link(c, m):
    args = m.text.split()
    if len(args) < 3:
        return await m.reply_text("Usage: `/setlink -100xxxxx https://t.me/+xxxx`")
    try:
        chat_id = int(args[1])
        link = args[2]
        await LinkData.update_one({'chat_id': chat_id}, {'$set': {'link': link}}, upsert=True)
        await m.reply_text(f"✅ Link set for `{chat_id}`")
    except Exception as e:
        await m.reply_text(f"Error: {e}")

# 2. START HANDLER
@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
    target_link = BACKUP_CHANNEL
    if len(m.text.split()) > 1:
        try:
            chat_id = int(m.text.split()[1])
            db_link = await LinkData.find_one({'chat_id': chat_id})
            if db_link: target_link = db_link['link']
        except: pass

    text = (
        "**HERE IS YOUR LINK! CLICK BELOW TO PROCEED**\n\n"
        "• **REQUEST TO JOIN** •\n\n"
        "**Note:** If the link is expired, please click the post link again."
    )
    buttons = [[InlineKeyboardButton("• REQUEST TO JOIN •", url=target_link)]]
    await m.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

# 3. AUTO ACCEPT
@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    chat_title = m.chat.title
    await c.approve_chat_join_request(chat_id, user_id)
    
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})

    db_link = await LinkData.find_one({'chat_id': chat_id})
    btn_link = db_link['link'] if db_link else BACKUP_CHANNEL
    
    accept_text = f"HEY {m.from_user.mention} ⚡️\n\nYOUR REQUEST TO JOIN **{chat_title}** HAS BEEN APPROVED. ✅"
    buttons = [[InlineKeyboardButton("• JOIN MY UPDATES •", url=BACKUP_CHANNEL)],
               [InlineKeyboardButton(f"• JOIN {chat_title} •", url=btn_link)]]
    try:
        await c.send_message(user_id, text=accept_text, reply_markup=InlineKeyboardMarkup(buttons))
    except: pass

# 4. ADMIN COMMANDS
@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(c, m):
    total = await Data.count_documents({})
    await m.reply_text(f"Total Users: {total}")

@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(c, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a message!")
    users = Data.find({})
    async for user in users:
        try: await m.reply_to_message.copy(user['id'])
        except: pass
    await m.reply_text("Done!")

Bot.run()
