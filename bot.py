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

# --- CONFIGURATION (Sahi format mein) ---
API_ID = 33568744
API_HASH = "362b41958aa6a949dbe789bbf82d01e8"
BOT_TOKEN = "8267135540:AAESIn5KuPL0rPl3vVTWsdm6b3axEGhCeao"
DB_URL = "mongodb+srv://princeverma:Pkgamingff347@tp-auto-aprove-bot.8hc3wp3.mongodb.net/?appName=TP-APROVE-BOT"

# ADMINS List (Bracket mein commas ke sath)
ADMINS = [8241838848, 7083049534] 

# Aapke bataye huye URLs
BACKUP_URL = "https://t.me/TP_Bot_Updates"
SUPPORT_URL = "https://t.me/TP_Chats_02"
TP_SERVER = "https://t.me/TP_Server_02"

# --- DATABASE ---
Dbclient = AsyncIOMotorClient(DB_URL)
Data = Dbclient['Cluster0']['users']
LinkData = Dbclient['Cluster0']['links']
Settings = Dbclient['Cluster0']['settings']

Bot = Client(name='TP_AutoBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. ADMIN COMMANDS (Pic aur Text ke liye)
@Bot.on_message(filters.command("setpic") & filters.user(ADMINS))
async def set_pic(c, m):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply_text("Photo ko reply karke `/setpic` likhein!")
    file_id = m.reply_to_message.photo.file_id
    await Settings.update_one({'id': 'config'}, {'$set': {'pic': file_id}}, upsert=True)
    await m.reply_text("✅ Approval Picture Updated!")

@Bot.on_message(filters.command("settext") & filters.user(ADMINS))
async def set_text(c, m):
    if len(m.text.split()) < 2: return await m.reply_text("Usage: `/settext Aapka Message` ")
    new_text = m.text.split(None, 1)[1]
    await Settings.update_one({'id': 'config'}, {'$set': {'text': new_text}}, upsert=True)
    await m.reply_text("✅ Welcome Text Updated!")

# 2. START HANDLER (With Auto-Delete & Note)
@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    
            # --- LINK GENERATE WALA LOGIC (REVISED) ---
        if len(m.text.split()) > 1:
            try:
                chat_id = int(m.text.split()[1])
                db_link = await LinkData.find_one({'chat_id': chat_id})
                target_link = db_link['link'] if db_link else TP_SERVER

                # Database se Admin ki set ki hui photo aur text nikalna
                config = await Settings.find_one({'id': 'config'})
                pic = config.get('pic') if config else None
                
                # Format jaisa aapne screenshot mein dikhaya
                text = f"**HERE IS YOUR LINK! CLICK BELOW TO PROCEED**\n\n• **REQUEST TO JOIN** •"
                note_text = "Note: If the link is expired, please click the post link again to get a new one."

                # Button se dots hataye gaye
                btn = [[
                    InlineKeyboardButton("REQUEST TO JOIN", url=target_link)
                ]]

                # Agar /setpic se photo set hai toh photo bhejega
                if pic:
                    msg = await c.send_photo(
                        m.chat.id,
                        photo=pic,
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                else:
                    msg = await m.reply_text(
                        text,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )

                # Note wala message alag se
                note_msg = await m.reply_text(note_text)

                # 3 Min Auto Delete Logic
                await asyncio.sleep(180)
                try:
                    await msg.delete()
                    await note_msg.delete()
                except:
                    pass
                return

            except Exception as e:
                print(f"Error in Start: {e}")
                # Agar error aaye toh fallback message
                await m.reply_text(f"❌ Error: Bot ko us channel mein Admin banayein!\n{e}")
                return


    # Simple Start Message
    text = f"Hai @{m.from_user.username} I am Auto Request Accept Bot. Add Me In Your Channel To Use"
    buttons = [[InlineKeyboardButton("Updates", url=BACKUP_URL), 
                InlineKeyboardButton("Support", url=SUPPORT_URL)]]
    await m.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# 3. LINK GENERATOR (Forward Message to Bot)
@Bot.on_message(filters.forwarded & filters.private & filters.user(ADMINS))
async def gen_link_forward(c, m):
    if not m.forward_from_chat: return
    chat_id = m.forward_from_chat.id
    try:
        link_obj = await c.create_chat_invite_link(chat_id, creates_join_request=True)
        link = link_obj.invite_link
        await LinkData.update_one({'chat_id': chat_id}, {'$set': {'link': link}}, upsert=True)
        
        bot_username = (await c.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={chat_id}"
        await m.reply_text(f"Here is your channel link :-\n\n`{share_link}`")
    except Exception as e:
        await m.reply_text(f"❌ Error: Bot ko us channel mein Admin banayein!\n{e}")

# 4. AUTO ACCEPT (With Pic + TP Server Link)
@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    await c.approve_chat_join_request(chat_id, user_id)
    
    config = await Settings.find_one({'id': 'config'})
    pic = config.get('pic') if config else None
    custom_text = config.get('text') if config else f"YOUR REQUEST TO JOIN **{m.chat.title}** HAS BEEN APPROVED."

    db_link = await LinkData.find_one({'chat_id': chat_id})
    ch_link = db_link['link'] if db_link else TP_SERVER

    text = f"HEY {m.from_user.mention} ⚡️\n\n{custom_text}"
    buttons = [[InlineKeyboardButton("• TP SERVER •", url=TP_SERVER)],
               [InlineKeyboardButton(f"• JOIN {m.chat.title} •", url=ch_link)]]
    
    try:
        if pic:
            await c.send_photo(user_id, photo=pic, caption=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await c.send_message(user_id, text=text, reply_markup=InlineKeyboardMarkup(buttons))
    except: pass

Bot.run()
