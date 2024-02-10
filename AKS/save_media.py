import asyncio
import traceback
from info import DB_CHANNEL, LOG_CHANNEL, BOT_USERNAME, BATCH_CHANNEL, BIN_CHANNEL, URL
from pyrogram import Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from AKS.helpers import str_to_b64, calc, get_size, get_hash
from AKS.database import db
    
async def forward_to_channel(bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.forward(DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
        return await forward_to_channel(bot, message, editable)

async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        forwarded_msg = await message.forward(DB_CHANNEL)
        getFile = await bot.get_messages(DB_CHANNEL, forwarded_msg.id)
        if getFile and getFile.document:
            file_name = getFile.document.file_name
            file_size = getFile.document.file_size
            duration = calc(getFile.document.duration) if hasattr(getFile.document, 'duration') else None
        elif getFile and getFile.video:
            file_name = getFile.video.file_name
            file_size = getFile.video.file_size
            duration = calc(getFile.video.duration) if hasattr(getFile.video, 'duration') else None
        elif getFile and getFile.audio:
            file_name = getFile.audio.file_name
            file_size = getFile.audio.file_size
            duration = calc(getFile.audio.duration) if hasattr(getFile.audio, 'duration') else None
        else:
            file_name = 'None'
            file_size = 'None'
            duration = 'None'
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        aks = await message.forward(BIN_CHANNEL)
        aks_file = await bot.get_messages(BIN_CHANNEL, aks.id)
        stream = f"https://{URL}/watch/{aks_file.id}?hash={get_hash(aks_file)}"
        short_link = await db.get_shortlink(user, stream)
        share_link = f"https://telegram.me/share/url?url={short_link}"
        caption = user.get('caption')
        default_caption = f"<b>ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀꜱᴛ ꜰʀᴏᴍ ʜᴇʀᴇ - {short_link}</b>"
        msg = caption.format(short_link=short_link, file_name=file_name, file_size=get_size(file_size), duration=duration) if caption else default_caption
        btn=[[
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ", url=short_link),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=share_link)
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        edited_thumb = await editable.edit_caption(
            caption=msg,
            reply_markup=reply_markup
        )
        if user.get("channel_ids"):
            for channel_id in user["channel_ids"]:
                await edited_thumb.copy(channel_id)
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
        await save_media_in_channel(bot, editable, message) 
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

async def save_batch_in_channel(bot: Client, message: Message, edit_txt: Message, linksList: list):
    try:
        userid = message.from_user.id
        user = await db.get_user(userid)
        batch = user.get("batch_channel")
        fileCount = int(linksList[1]) - int(linksList[0])
        i = 1
        while (i<fileCount):
            linksList += [(int(linksList[0])+i)]
            i+=1
        linksList.sort()
        msg_ids = ""
        for msg in (await bot.get_messages(chat_id=batch, message_ids=linksList)):
            if msg is None:
                continue
            to_DB = await msg.forward(DB_CHANNEL)
            if to_DB is not None:
                msg_ids += f"{to_DB.id} "
            else:
                continue
        msg = await bot.send_message(
            chat_id=DB_CHANNEL,
            text=msg_ids,
            disable_web_page_preview=True
        )
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        link = f"https://telegram.me/{BOT_USERNAME}?start=Aks_{str_to_b64(str(msg.id))}"
        short_link = await db.get_shortlink(user, link)
        share_link = f"https://telegram.me/share/url?url={short_link}"
        btn = [[
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ", url=short_link),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=share_link)
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        msg = await edit_txt.edit_caption(
            caption=f"**Batch Files Stored in my Database!**\n\nHere is the Permanent Link of your files: `{short_link}` \n\nJust Click the link to get your files!",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        if user.get("channel_ids"):
            for channel_id in user["channel_ids"]:
               await msg.copy(channel_id) 
    except Exception as err:
        print(err)
        await edit_txt.edit_caption(
            caption=f"Something Went Wrong!\n\n**Error:** `{err}`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
