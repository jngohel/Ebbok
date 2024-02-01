import asyncio
import requests
import string
import random
from info import DB_CHANNEL, FORWARD_AS_COPY, BOT_USERNAME
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
from handlers.database import db
import traceback

def s2time(time):
    hr = time//3600
    mint = (time-(hr*3600))//60
    sec = (time-3600) - (60*((time-3600)//60))
    return f"{hr}:{mint}:{sec}"

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def reply_forward(message: Message, file_id: int):
    try:
        await message.reply_text(
            f"Files will be deleted in 30 minutes to avoid copyright issues. Please forward and save them.",
            disable_web_page_preview=True,
            quote=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await reply_forward(message, file_id)

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
                        duration = s2time(file.document.duration) if hasattr(file.document, 'duration') else None
                    elif file and file.video:
                        file_name = file.video.file_name
                        file_size = file.video.file_size
                        file_id = file.video.file_id
                        duration = s2time(file.video.duration) if hasattr(file.video, 'duration') else None
                    elif file and file.audio:
                        file_name = file.audio.file_name
                        file_size = file.audio.file_size
                        file_id = file.audio.file_id
                        duration = s2time(file.audio.duration) if hasattr(file.audio, 'duration') else None
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
                    file_er_id = str(file_id)
                    share_link = f"https://telegram.me/{BOT_USERNAME}?start=VJBotz_{str_to_b64(file_er_id)}"
                    short_link = await db.get_shortlink(user, share_link)

                    return await bot.send_cached_media(
                        chat_id=user_id,
                        file_id=file_id,
                        caption=user['caption'].format(
                            file_name=file_name,
                            file_size=get_size(file_size),
                            duration=duration,
                            short_link=short_link
                        ) if duration else user['caption'].format(
                            file_name=file_name,
                            file_size=get_size(file_size),
                            short_link=short_link
                        )
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    return await media_forward(bot, user_id, file_id)
                except Exception as e:
                    print(f"File send error: {e}")
                    print(traceback.format_exc())
            else:
                return await bot.forward_messages(
                    chat_id=user_id,
                    from_chat_id=DB_CHANNEL,
                    message_ids=file_id
                )
    except Exception as e:
        print(f"Error in media_forward: {e}")

async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    sent_message = await media_forward(bot, user_id, file_id)
    await reply_forward(message=sent_message, file_id=file_id)
    asyncio.create_task(delete_after_delay(sent_message, 1800))

async def delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()
