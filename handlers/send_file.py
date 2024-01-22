import asyncio
import requests
import string
import random
from info import DB_CHANNEL, FORWARD_AS_COPY
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
from database import db as dbObject

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
            return await bot.copy_message(
                chat_id=user_id, 
                from_chat_id=DB_CHANNEL,
                message_id=file_id
            )
        elif FORWARD_AS_COPY is False:
            userObject = await dbObject.get_user(user_id)
            if userObject and 'caption' in userObject.keys():
                fileObject = await bot.get_messages(
                    chat_id=DB_CHANNEL,
                    message_ids=file_id
                )
                if fileObject and fileObject.document:
                    f_name = fileObject.document.file_name
                elif fileObject and fileObject.video:
                    f_name = fileObject.video.file_name
                elif fileObject and fileObject.audio:
                    f_name = fileObject.audio.file_name
                else:
                    return await bot.forward_messages(
                        chat_id=user_id, 
                        from_chat_id=DB_CHANNEL,
                        message_ids=file_id
                    )
                return await bot.send_cached_media(
                    chat_id=user_id,
                    file_id=file_id,
                    caption=userObject['caption'].format(
                        file_name=f_name
                    )
                )
            else:
                return await bot.forward_messages(
                    chat_id=user_id, 
                    from_chat_id=DB_CHANNEL,
                    message_ids=file_id
                )


    except FloodWait as e:
        await asyncio.sleep(e.value)
        return media_forward(bot, user_id, file_id)
        await message.delete()

async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    sent_message = await media_forward(bot, user_id, file_id)
    await reply_forward(message=sent_message, file_id=file_id)
    asyncio.create_task(delete_after_delay(sent_message, 1800))

async def delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()
