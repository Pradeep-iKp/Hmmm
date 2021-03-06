import os
import asyncio
import logging
import logging.config

# Get logging configurations
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ListenerCanceled
from database.database import *
from config import *

BATCH = []


@Client.on_message(filters.command('start') & filters.incoming & filters.private)
async def start(c, m, cb=False):
    if not cb:
        send_msg = await m.reply_text("**πΆββοΈ Processing...**", quote=True)

    owner = await c.get_users(int(OWNER_ID))
    owner_username = owner.username if owner.username else 'Ns_bot_updates'

    # start text
    text = f"""Hey! {m.from_user.mention(style='md')} π 

π‘ ** --I'm Telegram File Store Bot!-- π€**

`You can store your any Telegram Media for Permanent Shareable Link!`\n\nβ  **Check Help**

**<| @HKrrish π¨βπ»\n..
"""


    # Buttons
    buttons = [
        [
            InlineKeyboardButton('Details π', url=f"https://telegra.ph/TG-File-Store-Bot-05-25-2"),
            InlineKeyboardButton('Help π‘', callback_data="help")
        ],
        [
            InlineKeyboardButton('About π', callback_data="about")
        ]
    ]

    # when button home is pressed
    if cb:
        return await m.message.edit(
                   text=text,
                   reply_markup=InlineKeyboardMarkup(buttons)
               )

    if len(m.command) > 1: # sending the stored file
        try:
            m.command[1] = await decode(m.command[1])
        except:
            pass

        if 'batch_' in m.command[1]:
            await send_msg.delete()
            cmd, chat_id, message = m.command[1].split('_')
            string = await c.get_messages(int(chat_id), int(message)) if not DB_CHANNEL_ID else await c.get_messages(int(DB_CHANNEL_ID), int(message))

            if string.empty:
                owner = await c.get_users(int(OWNER_ID))
                return await m.reply_text(f"π₯΄ **Sorry Sir, your file was deleted!** π\n\n**--Reason--** :\n1. If you stored camrips, adults files, Bot Deleted.\n2. Or Deleted by file Owner.")
            message_ids = (await decode(string.text)).split('-')
            for msg_id in message_ids:
                msg = await c.get_messages(int(chat_id), int(msg_id)) if not DB_CHANNEL_ID else await c.get_messages(int(DB_CHANNEL_ID), int(msg_id))

                if msg.empty:
                    owner = await c.get_users(int(OWNER_ID))
                    return await m.reply_text(f"π₯΄ **Sorry Sir, your file was deleted!** π\n\n**--Reason--** :\n1. If you stored camrips, adults files, Bot Deleted.\n2. Or Deleted by file Owner.")

                await msg.copy(m.from_user.id)
                await asyncio.sleep(1)
            return

        chat_id, msg_id = m.command[1].split('_')
        msg = await c.get_messages(int(chat_id), int(msg_id)) if not DB_CHANNEL_ID else await c.get_messages(int(DB_CHANNEL_ID), int(msg_id))

        if msg.empty:
            return await send_msg.edit(f"π₯΄ **Sorry Sir, your file was deleted!** π\n\n**--Reason--** :\n1. If you stored camrips, adults files, Bot Deleted.\n2. Or Deleted by file Owner.")
        
        caption = f"{msg.caption.markdown}\n\n\n" if msg.caption else ""
        as_uploadername = (await get_data(str(chat_id))).up_name
        
        if as_uploadername:
            if chat_id.startswith('-100'):
                channel = await c.get_chat(int(chat_id))
                caption += "**--Uploader Details-- :**\n\n" 
                caption += f"**π’ Channel Name :** `{channel.title}`\n" 
                caption += f"**π£ User Name :** @{channel.username}\n" if channel.username else "" 
                caption += f"**π€ Channel Id :** `{channel.id}`\n\n" 
                caption += f"**π¬ DC ID :** {channel.dc_id}\n\n" if channel.dc_id else "" 
                caption += f"**π₯ Members Count :** {channel.members_count}\n\n" if channel.members_count else ""
            else:
                user = await c.get_users(int(chat_id)) 
                caption += "**--Uploader Details-- :**\n\n" 
                caption += f"**π First Name :** `{user.first_name}`\n" 
                caption += f"**π Last Name :** `{user.last_name}`\n" if user.last_name else "" 
                caption += f"**π₯ User Name :** @{user.username}\n" if user.username else "" 
                caption += f"**π€ User Id :** `{user.id}`\n\n" 
                caption += f"**π¬ DC ID :** {user.dc_id}\n\n" if user.dc_id else ""


        await send_msg.delete()
        await msg.copy(m.from_user.id, caption=caption)


    else: # sending start message
        await send_msg.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@Client.on_message(filters.command('me') & filters.incoming & filters.private)
async def me(c, m):
    """ This will be sent when /me command was used"""

    me = await c.get_users(m.from_user.id)
    text = "--**β’ Your Info β’**--\n\n"
    text += f"**π First Name :** `{me.first_name}`\n"
    text += f"**π Last Name :** `{me.last_name}`\n" if me.last_name else ""
    text += f"**π₯ User Name :** @{me.username}\n\n" if me.username else ""
    text += f"**π€ User Id :** `{me.id}`\n"
    text += f"**π¬ DC ID :** {me.dc_id}\n\n" if me.dc_id else ""
    text += f"**β Is Verified By TELEGRAM :** `{me.is_verified}`\n" if me.is_verified else ""
    text += f"**πΊ Is Fake :** {me.is_fake}\n" if me.is_fake else ""
    text += f"**π¨ Is Scam :** {me.is_scam}\n\n" if me.is_scam else ""
    text += f"**π Language Code :** `{me.language_code}`\n\n" if me.language_code else ""

    await m.reply_text(text, quote=True)


@Client.on_message(filters.command('batch') & filters.private & filters.incoming)
async def batch(c, m):
    """ This is for batch command"""
    if IS_PRIVATE:
        if m.from_user.id not in AUTH_USERS:
            return
    BATCH.append(m.from_user.id)
    files = []
    i = 1

    while m.from_user.id in BATCH:
        if i == 1:
            media = await c.ask(chat_id=m.from_user.id, text='--**β’ Here you can generate batch files link β’**--\n\nJust Send me some files, videos, photos, text, audio, stickers, etc.\n\nIf you want to cancel the process send /cancel')
            if media.text == "/cancel":
                return await m.reply_text('Cancelled Successfully β')
            files.append(media)
        else:
            try:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Done β', callback_data='done')]])
                media = await c.ask(chat_id=m.from_user.id, text='Ok π. Now send me some more files Or press done to get shareable link.\n\nIf you want to cancel the process send /cancel', reply_markup=reply_markup)
                if media.text == "/cancel":
                    return await m.reply_text('Cancelled Successfully β')
                files.append(media)
            except ListenerCanceled:
                pass
            except Exception as e:
                print(e)
                await m.reply_text(text="Something went wrong. Try again later.")
        i += 1

    message = await m.reply_text("**Please wait..!** Generating your shareable link π")
    string = ""
    for file in files:
        if DB_CHANNEL_ID:
            copy_message = await file.copy(int(DB_CHANNEL_ID))
        else:
            copy_message = await file.copy(m.from_user.id)
        string += f"{copy_message.message_id}-"
        await asyncio.sleep(1)

    string_base64 = await encode_string(string[:-1])
    send = await c.send_message(m.from_user.id, string_base64) if not DB_CHANNEL_ID else await c.send_message(int(DB_CHANNEL_ID), string_base64)
    base64_string = await encode_string(f"batch_{m.chat.id}_{send.message_id}")
    bot = await c.get_me()
    url = f"**--β’ Here is Your batch link β’--**\n\nπ : https://t.me/{bot.username}?start={base64_string}\n\n**Save It!**"

    await message.edit(text=url)

@Client.on_message(filters.command('mode') & filters.incoming & filters.private)
async def set_mode(c,m):
    if IS_PRIVATE:
        if m.from_user.id not in AUTH_USERS:
            return
    usr = m.from_user.id
    if len(m.command) > 1:
        usr = m.command[1]
    caption_mode = (await get_data(usr)).up_name
    if caption_mode:
       await update_as_name(str(usr), False)
       text = "Uploader Details in Caption : **Disabled β**"
    else:
       await update_as_name(str(usr), True)
       text = "Uploader Details in Caption : **Enabled β**"
    await m.reply_text(text, quote=True)

async def decode(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def encode_string(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string
