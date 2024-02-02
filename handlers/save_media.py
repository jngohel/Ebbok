import asyncio
from info import DB_CHANNEL, LOG_CHANNEL, BOT_USERNAME
from pyrogram import Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
from handlers.send_file import get_size, s2time
import traceback
from handlers.database import db
    
async def forward_to_channel(bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.forward(DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                disable_web_page_preview=True
            )
        return await forward_to_channel(bot, message, editable)

async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        msg = await editable.edit_caption(
            caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(5)
        forwarded_msg = await message.forward(DB_CHANNEL)
        getFile = await bot.get_messages(DB_CHANNEL, forwarded_msg.id)
        if getFile and getFile.document:
            file_name = getFile.document.file_name
            file_size = getFile.document.file_size
            duration = s2time(getFile.document.duration) if hasattr(getFile.document, 'duration') else None
        elif getFile and getFile.video:
            file_name = getFile.video.file_name
            file_size = getFile.video.file_size
            duration = s2time(getFile.video.duration) if hasattr(getFile.video, 'duration') else None
        elif getFile and getFile.audio:
            file_name = getFile.audio.file_name
            file_size = getFile.audio.file_size
            duration = s2time(getFile.audio.duration) if hasattr(getFile.audio, 'duration') else None
        else:
            file_name = 'None'
            file_size = 'None'
            duration = 'None'
        file_er_id = str(forwarded_msg.id)
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        direct_file = f"https://telegram.me/{BOT_USERNAME}?start=Aks_{str_to_b64(file_er_id)}"
        share_link = f"https://telegram.me/{BOT_USERNAME}?start=Aks_{str_to_b64(file_er_id)}"
        short_link = await db.get_shortlink(user, share_link)
        share_link = f"https://telegram.me/share/url?url={short_link}"
        caption = user.get('caption')
        default_caption = f"<b>ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀꜱᴛ ꜰʀᴏᴍ ʜᴇʀᴇ - {short_link}</b>"
        msg = caption.format(short_link=short_link, file_name=file_name, file_size=get_size(file_size), duration=duration) if caption else default_caption
        pm_btn = [[
            InlineKeyboardButton("ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ", url=direct_file),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=share_link)
        ]]
        channel_btn = [[
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ", url=short_link),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=share_link)
        ]]
        if user.get("channel_id"):
            channel_id = user["channel_id"]
            if message.chat.type == enums.ChatType.PRIVATE:
                reply_markup = InlineKeyboardMarkup(pm_btn)
            else:
                reply_markup = InlineKeyboardMarkup(channel_btn)
        edited_thumb = await editable.edit_caption(
            caption=msg,
            reply_markup=reply_markup
        )
        if user.get("channel_id"):
            await edited_thumb.copy(channel_id)
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
        await save_media_in_channel(bot, editable, message)
    except Exception as err:
        print(traceback.format_exc())
        await editable.edit_caption(
            caption=f"Something Went Wrong!\n\n**Error:** `{err}`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list):
    try:
        message_ids_str = ""
        for message in (await bot.get_messages(chat_id=editable.chat.id, message_ids=message_ids)):
            sent_message = await forward_to_channel(bot, message, editable)
            if sent_message is None:
                continue
            message_ids_str += f"{str(sent_message.id)} "
            await asyncio.sleep(2)
            await editable.edit_caption(
                caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>",
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(5)
        msg = await bot.send_message(
            chat_id=DB_CHANNEL,
            text=message_ids_str,
            disable_web_page_preview=True
        )
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        share_link = f"https://telegram.me/{BOT_USERNAME}?start=VJBotz_{str_to_b64(str(msg.id))}"
        short_link = await db.get_shortlink(user, share_link)
        #share_link = f"https://telegram.me/share/url?url={short_link}"
        btn = [[
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ", url=short_link),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=share_link)
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        caption = f"<b>Batch Files Stored in Database!\n\n{short_link}\n\n</b>"
        await editable.edit_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=reply_markup
        )
    except Exception as err:
        print(err)
        await editable.edit_caption(
            caption=f"Something Went Wrong!\n\n**Error:** `{err}`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
