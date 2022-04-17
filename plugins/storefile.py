import os
import urllib
from .commands import encode_string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import *


# @Client.on_message(filters.command(['link', 'store']) & ~filters.edited)
# def storefile(bot, message):
  #  replied = message.reply_to_message
  #  if not replied:
   #     return await message.reply('hmm')
   # file_type = replied.media
  #  if file_type not in ["photo", "video", 'audio', 'document']:
   #     return await message.reply('Hm')
   # bot = await c.get_me()
   # base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
  #  url = f"https://t.me/{bot.username}?start={base64_string}"
   # await message.reply(f"Here is Link : {url}")
    
    







#################################### FOR PRIVATE ################################################
@Client.on_message((filters.document|filters.video|filters.audio|filters.photo) & filters.incoming & ~filters.edited & ~filters.channel)
async def storefile(c, m):
    if IS_PRIVATE:
        if m.from_user.id not in AUTH_USERS:
            return
    send_message = await m.reply_text("**🚶‍♂️ Processing...**", quote=True)
    media = m.document or m.video or m.audio or m.photo
    # text
    text = ""
    if not m.photo:
        text = "**--• Link Generated •--**\n\n**🗃️ --File Details-- :**\n\n"
        text += f"📂 **File Name :** `{media.file_name}`\n" if media.file_name else ""
        text += f"💽 **Mime Type :** `{media.mime_type}`\n" if media.mime_type else ""
        text += f"📊 **File Size :** `{humanbytes(media.file_size)}`\n\n" if media.file_size else ""
        if not m.document:
            text += f"🎞 **Duration :** `{TimeFormatter(media.duration * 1000)}`\n\n" if media.duration else ""
            if m.audio:
                text += f"🎵 **Title :** `{media.title}`\n" if media.title else ""
                text += f"🎙 **Performer :** `{media.performer}`\n\n" if media.performer else ""
    text += f"**✏ Caption :** `{m.caption}`\n\n" if m.caption else ""
    text += "**--Uploader Details-- :**\n\n"
    text += f"**🙂 First Name :** `{m.from_user.first_name}`\n"
    text += f"**🙃 Last Name :** `{m.from_user.last_name}`\n" if m.from_user.last_name else ""
    text += f"**💥 User Name :** @{m.from_user.username}\n" if m.from_user.username else ""
    text += f"**👤 User Id :** `{m.from_user.id}`\n\n"
    text += f"**💬 DC ID :** {m.from_user.dc_id}\n\n" if m.from_user.dc_id else ""

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('', ''))
    share_url = f"tg://share?url={txt}File%20Link%20👉%20{url}"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="Open Url 🔗", url=url),
        InlineKeyboardButton(text="Share Link 👤", url=share_url)
        ],[
        InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete+{msg.message_id}")
    ]]

    # sending message
    await send_message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

#################################### FOR CHANNEL################################################

@Client.on_message((filters.document|filters.video|filters.audio|filters.photo) & filters.incoming & filters.channel & ~filters.forwarded & ~filters.edited)
async def storefile_channel(c, m):
    if IS_PRIVATE:
        if m.chat.id not in AUTH_USERS:
            return
    media = m.document or m.video or m.audio or m.photo

    # text
    text = ""
    if not m.photo:
        text = "**🗃️ --File Details-- :**\n\n"
        text += f"📂 **File Name :** `{media.file_name}`\n" if media.file_name else ""
        text += f"💽 **Mime Type :** `{media.mime_type}`\n" if media.mime_type else ""
        text += f"📊 **File Size :** `{humanbytes(media.file_size)}`\n\n" if media.file_size else ""
        if not m.document:
            text += f"🎞 **Duration :** `{TimeFormatter(media.duration * 1000)}`\n\n" if media.duration else ""
            if m.audio:
                text += f"🎵 **Title :** `{media.title}`\n" if media.title else ""
                text += f"🎙 **Performer :** `{media.performer}`\n\n" if media.performer else ""
    text += f"**✏ Caption :** `{m.caption}`\n\n"
    text += "**--Uploader Details-- :**\n\n"
    text += f"**📢 Channel Name :** `{m.chat.title}`\n"
    text += f"**🗣 User Name :** @{m.chat.username}\n" if m.chat.username else ""
    text += f"**👤 Channel Id :** `{m.chat.id}`\n\n"
    text += f"**💬 DC ID :** {m.chat.dc_id}\n\n" if m.chat.dc_id else ""
    text += f"**👥 Members Count :** {m.chat.members_count}\n\n" if m.chat.members_count else ""

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('', ''))
    share_url = f"tg://share?url={txt}File%20Link%20👉%20{url}"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="Open Url 🔗", url=url),
        InlineKeyboardButton(text="Share Link 👤", url=share_url)
    ]]

    # Editing and adding the buttons
    await m.edit_reply_markup(InlineKeyboardMarkup(buttons))


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " days, ") if days else "") + \
        ((str(hours) + " hrs, ") if hours else "") + \
        ((str(minutes) + " min, ") if minutes else "") + \
        ((str(seconds) + " sec, ") if seconds else "") + \
        ((str(milliseconds) + " millisec, ") if milliseconds else "")
    return tmp[:-2]
