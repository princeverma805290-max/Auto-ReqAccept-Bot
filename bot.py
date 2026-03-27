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

# --- CONFIGURATION (Prince Bhai Details) ---
API_ID = 33568744
API_HASH = "362b41958aa6a949dbe789bbf82d01e8"
BOT_TOKEN = "8267135540:AAESIn5KuPL0rPl3vVTWsdm6b3axEGhCeao"
DB_URL = "mongodb+srv://princeverma:Pkgamingff347@tp-auto-aprove-bot.8hc3wp3.mongodb.net/?appName=TP-APROVE-BOT"
ADMINS = 8241838848
BACKUP_CHANNEL = "https://t.me/TP_Bot_Updates" # Aapka backup channel

# --- DATABASE & BOT ---
Dbclient = AsyncIOMotorClient(DB_URL)
Data = Dbclient['Cluster0']['users']
Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. START COMMAND (Exact Video Layout)
@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
    text = (
        "**HERE IS YOUR LINK! CLICK BELOW TO PROCEED**\n\n"
        "• **REQUEST TO JOIN** •\n\n"
        "**Note:** If the link is expired, please click the post link again to get a new one."
    )
    # Yahan apne main channel ka link (+) wala dalein
    buttons = [[InlineKeyboardButton("• REQUEST TO JOIN •", url="https://t.me/HENTAI_HUB_02")]] 
    await m.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

# 2. AUTO ACCEPT & STYLISH MSG
@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_title = m.chat.title
    await c.approve_chat_join_request(m.chat.id, user_id)
    
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})

    accept_text = (
        f"HEY {m.from_user.mention} ⚡️\n\n"
        f"YOUR REQUEST TO JOIN **{chat_title}** HAS BEEN APPROVED. ✅"
    )
    buttons = [
        [InlineKeyboardButton("• JOIN MY UPDATES •", https://t.me/HENTAI_HUB_02)],
        [InlineKeyboardButton(f"• JOIN {chat_title} •", url=BACKUP_CHANNEL)] # Channel link as backup
    ]
    try:
        await c.send_message(chat_id=user_id, text=accept_text, reply_markup=InlineKeyboardMarkup(buttons))
    except: pass

# 3. PRO BROADCAST (Copy formatting and quotes)
@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_handler(c, m):
    if not m.reply_to_message:
        return await m.reply_text("Pehle kisi message ka **Reply** karein jise broadcast karna hai!")
    
    msg = await m.reply_text("Broadcast shuru ho raha hai... 🚀")
    users = Data.find({})
    success = 0
    failed = 0
    
    async for user in users:
        try:
            # copy() function formatting aur quotes ko waisa hi rakhta hai
            await m.reply_to_message.copy(chat_id=user['id'])
            success += 1
            await asyncio.sleep(0.1) # Bot ban se bachne ke liye
        except:
            failed += 1
            
    await msg.edit(f"**Broadcast Complete!** ✅\n\n**Success:** `{success}`\n**Failed:** `{failed}`")

# 4. STATS COMMAND
@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(c, m):
    total = await Data.count_documents({})
    await m.reply_text(f"📊 **Bot Statistics:**\n\n**Total Users:** `{total}`")

Bot.run()
