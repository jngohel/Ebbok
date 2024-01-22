import asyncio
from info import DB_CHANNEL, LOG_CHANNEL, BOT_USERNAME
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
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
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        return await forward_to_channel(bot, message, editable)

async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        msg = await editable.edit("<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>")
        await asyncio.sleep(5)
        await msg.delete()
        forwarded_msg = await message.forward(DB_CHANNEL)
        file_er_id = str(forwarded_msg.id)
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        share_link = f"https://telegram.me/{BOT_USERNAME}?start=VJBotz_{str_to_b64(file_er_id)}"
        short_link = await db.get_shortlink(user, share_link)
        btn = [[
            InlineKeyboardButton("ᴏᴘᴇɴ ʟɪɴᴋ", url=share_link),
            InlineKeyboardButton("ꜱʜᴀʀᴇ ʟɪɴᴋ", url=short_link)
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await editable.reply_text(
            text=f"<b>ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀꜱᴛ ꜰʀᴏᴍ ʜᴇʀᴇ - {short_link}</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(LOG_CHANNEL),
                text="#FloodWait:\n"
                     f"Got FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")
                        ]
                    ]
                )
            )
        await save_media_in_channel(bot, editable, message)
    except Exception as err:
        print(err)
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        await bot.send_message(
            chat_id=int(LOG_CHANNEL),
            text="#ERROR_TRACEBACK:\n"
                 f"Got Error from `{str(editable.chat.id)}` !!\n\n"
                 f"**Traceback:** `{err}`",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")
                    ]
                ]
            )
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
            msg = await editable.edit("<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>")
            await asyncio.sleep(5)
            await msg.delete()
        msg = await bot.send_message(
            chat_id=DB_CHANNEL,
            text=message_ids_str,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Delete Batch", callback_data="closeMessage")
                    ]
                ]
            )
        )
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        share_link = f"https://telegram.me/{BOT_USERNAME}?start=VJBotz_{str_to_b64(str(msg.id))}"
        short_link = await db.get_shortlink(user, share_link)
        await editable.reply_text(
            f"**Batch Files Stored in my Database!**\n\nHere is the Permanent Link of your files: <code>{short_link}</code> \n\n"
            f"Just Click the link to get your files!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Original Link", url=share_link),
                        InlineKeyboardButton("Short Link", url=short_link)
                    ]
                ]
            ),
            disable_web_page_preview=True
        )
        await bot.send_message(
            chat_id=int(LOG_CHANNEL),
            text=f"#BATCH_SAVE:\n\n[{editable.reply_to_message.from_user.first_name}](tg://user?id={editable.reply_to_message.from_user.id}) Got Batch Link!",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Original Link", url=short_link),
                        InlineKeyboardButton("Short Link", url=share_link)
                    ]
                ]
            )
        )
    except Exception as err:
        print(err)
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        await bot.send_message(
            chat_id=int(LOG_CHANNEL),
            text=f"#ERROR_TRACEBACK:\nGot Error from `{str(editable.chat.id)}` !!\n\n**Traceback:** `{err}`",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")
                    ]
                ]
            )
        )
