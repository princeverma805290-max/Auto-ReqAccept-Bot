import os, asyncio, threading
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

# Yahan aap aur admins ki ID add kar sakte hain comma lagakar
ADMINS = [8241838848, 123456789] 

BACKUP_URL = "https://t.me/TP_Server_02"

# --- DATABASE ---
Dbclient = AsyncIOMotorClient(DB_URL)
Data = Dbclient['Cluster0']['users']
LinkData = Dbclient['Cluster0']['links']

Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. GENERATE LINK (For any channel)
@Bot.on_message(filters.command("genlink") & filters.group)
async def gen_link(c, m):
    if m.from_user.id not in ADMINS: return
    chat_id = m.chat.id
    try:
        link_obj = await c.create_chat_invite_link(chat_id, creates_join_request=True)
        link = link_obj.invite_link
        await LinkData.update_one({'chat_id': chat_id}, {'$set': {'link': link}}, upsert=True)
        
        bot_username = (await c.get_me()).username
        shareable_link = f"https://t.me/{bot_username}?start={chat_id}"
        await m.reply_text(f"✅ **Link Generated!**\n\n**Join Link:** `{link}`\n\n**Bot Start Link:**\n`{shareable_link}`")
    except Exception as e:
        await m.reply_text(f"Bot ko Admin banayein with Invite Link permission! Error: {e}")

# 2. START HANDLER (Exact Video Layout)
@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
    target_link = BACKUP_URL
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

# 3. AUTO ACCEPT (Video Style)
@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    chat_title = m.chat.title
    await c.approve_chat_join_request(chat_id, user_id)
    
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})

    db_link = await LinkData.find_one({'chat_id': chat_id})
    ch_link = db_link['link'] if db_link else BACKUP_URL

    accept_text = f"HEY {m.from_user.mention} ⚡️\n\nYOUR REQUEST TO JOIN **{chat_title}** HAS BEEN APPROVED. ✅"
    buttons = [[InlineKeyboardButton("• JOIN MY UPDATES •", url=BACKUP_URL)],
               [InlineKeyboardButton(f"• JOIN {chat_title} •", url=ch_link)]]
    try:
        await c.send_message(user_id, text=accept_text, reply_markup=InlineKeyboardMarkup(buttons))
    except: pass

# 4. ADMIN COMMANDS (Broadcast & Stats)
@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(c, m):
    if not m.reply_to_message: return await m.reply_text("Reply to a message to broadcast!")
    msg = await m.reply_text("Broadcasting... 🚀")
    users = Data.find({})
    count = 0
    async for user in users:
        try:
            await m.reply_to_message.copy(user['id'])
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await msg.edit(f"✅ Sent to `{count}` users.")

@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(c, m):
    total = await Data.count_documents({})
    await m.reply_text(f"📊 Total Users: `{total}`")

Bot.run()
