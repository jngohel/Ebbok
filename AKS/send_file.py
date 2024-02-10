import asyncio
import traceback
import requests
import string
import random
from info import DB_CHANNEL, FORWARD_AS_COPY, BOT_USERNAME, DELETE_TIME, BIN_CHANNEL, URL
from pyrogram import Client
from pyrogram.types import Message 
from pyrogram.errors import FloodWait
from AKS.helpers import str_to_b64, get_readable_time, calc, get_size, get_hash
from AKS.database import db

DLT_SCHEDULE = {}

async def reply_forward(bot: Client, userID: int | str):
    try:
        await bot.send_message(
            chat_id=int(userID),
            text=f"<b>🚫 ɴᴏᴛᴇ - ꜰɪʟᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪꜱꜱᴜᴇꜱ. ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴏʀ ꜱᴀᴠᴇ ᴛʜᴇᴍ.</b>",
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await reply_forward(bot, userID)

async def media_forward(bot: Client, user_id: int, file_id: int):
    try:
        if FORWARD_AS_COPY is True:
            forwarded_msg = await bot.copy_message(
                chat_id=user_id,
                from_chat_id=DB_CHANNEL,
                message_id=file_id
            )
        elif FORWARD_AS_COPY is False:
            user = await db.get_user(user_id)
            if user and 'caption' in user.keys():
                try:
                    file = await bot.get_messages(
                        chat_id=DB_CHANNEL,
                        message_ids=file_id
                    )
                except Exception as e:
                    print(f"File fetch error: {e}")
                    return
                try:
                    if file and file.document:
                        file_name = file.document.file_name
                        file_size = file.document.file_size
                        file_id = file.document.file_id
                        duration = calc(file.document.duration) if hasattr(file.document, 'duration') else None
                    elif file and file.video:
                        file_name = file.video.file_name
                        file_size = file.video.file_size
                        file_id = file.video.file_id
                        duration = calc(file.video.duration) if hasattr(file.video, 'duration') else None
                    elif file and file.audio:
                        file_name = file.audio.file_name
                        file_size = file.audio.file_size
                        file_id = file.audio.file_id
                        duration = calc(file.audio.duration) if hasattr(file.audio, 'duration') else None
                    else:
                        return await bot.forward_messages(
                            chat_id=user_id,
                            from_chat_id=DB_CHANNEL,
                            message_ids=file_id
                        )
                except Exception as e:
                    print(f"File info fetch error: {e}")
                    return
                try:
                    aks = await bot.forward_messages(
                        chat_id=BIN_CHANNEL,
                        from_chat_id=DB_CHANNEL,
                        message_ids=file_id
                    )
                    aks_file = await bot.get_messages(BIN_CHANNEL, message_ids=aks.id)
                    stream = f"https://{URL}/watch/{aks_file.id}{file_name}?hash={get_hash(aks_file)}"
                    btn = [[
                        InlineKeyboardButton("ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ", url=stream)
                    ]]
                    reply_markup = InlineKeyboardMarkup(btn)
                    file_er_id = str(file_id)
                    share_link = f"https://telegram.me/{BOT_USERNAME}?start=Aks_{str_to_b64(file_er_id)}"
                    return await bot.send_cached_media(
                        chat_id=user_id,
                        file_id=file_id,
                        caption=user['caption'].format(
                            file_name=file_name,
                            file_size=get_size(file_size),
                            duration=duration,
                            short_link=short_link
                        ),
                        reply_markup=reply_markup
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    return await media_forward(bot, user_id, file_id)
                except Exception as e:
                    print(f"File send error: {e}")
                    print(traceback.format_exc())
            else:
                aks = await bot.forward_messages(
                    chat_id=BIN_CHANNEL,
                    from_chat_id=DB_CHANNEL,
                    message_ids=file_id
                )
                aks_file = await bot.get_messages(BIN_CHANNEL, message_ids=aks.id)
                stream = f"https://{URL}/watch/{aks_file.id}{file_name}?hash={get_hash(aks_file)}"
                btn = [[
                    InlineKeyboardButton("ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ", url=stream)
                ]]
                reply_markup = InlineKeyboardMarkup(btn)
                return await bot.forward_messages(
                    chat_id=user_id,
                    from_chat_id=DB_CHANNEL,
                    message_ids=file_id,
                    reply_markup=reply_markup
                )
    except Exception as e:
        print(f"Error in media_forward: {e}")

async def send_media_and_reply(bot: Client, user_id: int, file_id: int, uniqStr: str):
    sent_message = await media_forward(bot, user_id, file_id)
    dlt_list = DLT_SCHEDULE.get(uniqStr)
    if not dlt_list:
        DLT_SCHEDULE[uniqStr] = [sent_message]
    else:
        dlt_list.append(sent_message)
        DLT_SCHEDULE[uniqStr] = dlt_list

async def delete_after_delay(uniqStr, delay):
    await asyncio.sleep(delay)
    dlt_list = DLT_SCHEDULE.get(uniqStr)
    if not dlt_list:
        return
    else:
        for msg in dlt_list:
            try:
                await msg.delete()
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await msg.delete()
        DLT_SCHEDULE[uniqStr] = []
