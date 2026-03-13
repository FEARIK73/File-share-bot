import nest_asyncio
nest_asyncio.apply()

import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- Force Join Check ----------------
async def check_join(client, user_id):
    try:
        await client.get_chat_member(FORCE_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        print("Bot must be admin in FORCE_CHANNEL!")
        return False
    except PeerIdInvalid:
        print("Bot cannot access the channel. Check FORCE_CHANNEL!")
        return False

# ---------------- Send File ----------------
async def send_file(client, chat_id, data):
    try:
        if data.startswith("single_"):
            msg_id = int(data.split("_")[1])
            await client.copy_message(chat_id, DATABASE_CHANNEL, msg_id)
        elif data.startswith("batch_"):
            _, start, end = data.split("_")
            for msg_id in range(int(start), int(end)+1):
                await client.copy_message(chat_id, DATABASE_CHANNEL, msg_id)
    except PeerIdInvalid:
        await client.send_message(chat_id, "Database channel not found or bot not added!")
    except ChatAdminRequired:
        await client.send_message(chat_id, "Bot must be admin in database channel!")

# ---------------- Start Command ----------------
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    data = message.command[1] if len(message.command) > 1 else None

    joined = await check_join(client, user_id)
    if not joined:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
            [InlineKeyboardButton("Try Again", callback_data=f"retry|{data}")]
        ])
        await message.reply("Join the channel first to get the file.", reply_markup=keyboard)
        return

    if data:
        await send_file(client, message.chat.id, data)

# ---------------- Retry Button ----------------
@app.on_callback_query(filters.regex("retry"))
async def retry(client, query):
    user_id = query.from_user.id
    data = query.data.split("|")[1]

    joined = await check_join(client, user_id)
    if not joined:
        await query.answer("Join channel first!", show_alert=True)
        return

    await query.message.delete()
    await send_file(client, query.message.chat.id, data)

# ---------------- Run Bot ----------------
async def main():
    await app.start()
    print("Bot Started Successfully!")
    await idle()

asyncio.get_event_loop().run_until_complete(main())
