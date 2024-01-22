import os
from telethon.tl.types import DocumentAttributeVideo
import asyncio
import traceback
from binascii import Error
from Script import script
from pyrogram import Client, enums, filters
from pyrogram.errors import UserNotParticipant, FloodWait, QueryIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from info import DB_CHANNEL, AUTH_CHANNEL, BANNED_USERS, API_HASH, API_ID, BOT_USERNAME, BOT_TOKEN, LOG_CHANNEL, OTHER_USERS_CAN_SAVE_FILE, BOT_OWNER, BANNED_CHAT_IDS, SUPPORT_GROUP_LINK, UPDATES_CHANNEL_LINK
from handlers.database import db
from handlers.add_user_to_db import add_user_to_database
from handlers.send_file import send_media_and_reply
from handlers.helpers import b64_to_str, str_to_b64
from handlers.check_user_status import handle_user_status
from handlers.force_sub_handler import handle_force_sub, get_invite_link
from handlers.save_media import save_media_in_channel, save_batch_media_in_channel

MediaList = {}

Bot = Client(
    name=BOT_USERNAME,
    in_memory=True,
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@Bot.on_message(filters.private)
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

@Bot.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):
    if cmd.from_user.id in BANNED_USERS:
        await cmd.reply_text("Sorry, You are banned.")
        return
    if AUTH_CHANNEL is not None:
        back = await handle_force_sub(bot, cmd)
        if back == 400:
            return    
    usr_cmd = cmd.text.split("_", 1)[-1]
    if usr_cmd == "/start":
        await add_user_to_database(bot, cmd)
        btn = [[
            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ", url=UPDATES_CHANNEL_LINK),
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP_LINK)
        ],[
            InlineKeyboardButton("🎲 ғᴇᴀᴛᴜʀᴇꜱ 🎲", callback_data="features")
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await cmd.reply_text(
            script.START_TEXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
    else:
        try:
            try:
                file_id = int(b64_to_str(usr_cmd).split("_")[-1])
            except (Error, UnicodeDecodeError):
                file_id = int(usr_cmd.split("_")[-1])
            GetMessage = await bot.get_messages(chat_id=DB_CHANNEL, message_ids=file_id)
            message_ids = []
            if GetMessage.text:
                message_ids = GetMessage.text.split(" ")
                _response_msg = await cmd.reply_text(
                    text=f"**Total Files:** `{len(message_ids)}`",
                    quote=True,
                    disable_web_page_preview=True
                )
            else:
                message_ids.append(int(GetMessage.id))
            for i in range(len(message_ids)):
                await send_media_and_reply(bot, user_id=cmd.from_user.id, file_id=int(message_ids[i]))
        except Exception as e:
            print(e)

@Bot.on_message((filters.document | filters.video | filters.audio | filters.photo) & ~filters.chat(DB_CHANNEL))
async def main(bot: Client, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        await add_user_to_database(bot, message)
        if AUTH_CHANNEL is not None:
            back = await handle_force_sub(bot, message)
            if back == 400:
                return
        if message.from_user.id in BANNED_USERS:
            await message.reply_text(
                text="Sorry, You are banned!",
                disable_web_page_preview=True)
            return
        if OTHER_USERS_CAN_SAVE_FILE is False:
            return
        btn = [[
            InlineKeyboardButton("ʙᴀᴛᴄʜ ʟɪɴᴋ", callback_data="genratebatchlink")
        ],[
            InlineKeyboardButton("ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ", callback_data="sharable_mode")
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await message.reply_text(
            text="<b>ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏꜱᴇ ʜᴇʀᴇ 👇</b>",
            reply_markup=reply_markup,
            quote=True,
            disable_web_page_preview=True
        )

    elif message.chat.type == enums.ChatType.CHANNEL:
        if (message.chat.id == int(LOG_CHANNEL)) or (message.chat.id == int(AUTH_CHANNEL)) or message.forward_from_chat or message.forward_from:
            return
        elif int(message.chat.id) in BANNED_CHAT_IDS:
            await bot.leave_chat(message.chat.id)
            return
        else:
            pass

        try:
            forwarded_msg = await message.forward(DB_CHANNEL)
            file_er_id = str(forwarded_msg.id)
            share_link = f"https://t.me/{BOT_USERNAME}?start=VJBotz_{str_to_b64(file_er_id)}"
            CH_edit = await bot.edit_message_reply_markup(
                message.chat.id, 
                message.id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ", url=share_link)
                        ]
                    ]
                )
            )
            if message.chat.username:
                await forwarded_msg.reply_text(
                    f"#CHANNEL_BUTTON:\n\n[{message.chat.title}](https://t.me/{message.chat.username}/{CH_edit.id}) Channel's Broadcasted File's Button Added!")
            else:
                private_ch = str(message.chat.id)[4:]
                await forwarded_msg.reply_text(
                    f"#CHANNEL_BUTTON:\n\n[{message.chat.title}](https://t.me/c/{private_ch}/{CH_edit.id}) Channel's Broadcasted File's Button Added!")
        except FloodWait as sl:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(message.chat.id)}` !!",
                disable_web_page_preview=True
            )
        except Exception as err:
            await bot.leave_chat(message.chat.id)
            await bot.send_message(
                chat_id=int(LOG_CHANNEL),
                text=f"#ERROR_TRACEBACK:\nGot Error from `{str(message.chat.id)}` !!\n\n**Traceback:** `{err}`",
                disable_web_page_preview=True
            )

@Bot.on_callback_query()
async def button(bot: Client, cmd: CallbackQuery):
    cb_data = cmd.data
    if "start" in cb_data:
        btn = [[
            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ", url=UPDATES_CHANNEL_LINK),
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP_LINK)
        ],[
            InlineKeyboardButton("🎲 ғᴇᴀᴛᴜʀᴇꜱ 🎲", callback_data="features")
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await cmd.message.edit(
            script.START_TEXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

    elif "features" in cb_data:
        btn = [[
            InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="start")
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await cmd.message.edit(
            script.FEATURES_TEXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

    elif "checksub" in cb_data:
        if AUTH_CHANNEL:
            if AUTH_CHANNEL.startswith("-100"):
                channel_chat_id = int(AUTH_CHANNEL)
            else:
                channel_chat_id = AUTH_CHANNEL
            try:
                user = await bot.get_chat_member(channel_chat_id, cmd.message.chat.id)
                if user.status == "kicked":
                    await cmd.message.edit(
                        text="Sorry Sir, You are Banned to use me.",
                        chat_id = cmd.from_user.id,
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                invite_link = await get_invite_link(bot, chat_id=channel_chat_id)
                await cmd.answer("I like Your Smartness But Don't Be Oversmart! 😑", show_alert=True,)
                return
            except Exception:
                await cmd.message.edit(
                    text="Something went Wrong.",
                    disable_web_page_preview=True
                )
                return
        btn = [[
            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ", url=UPDATES_CHANNEL_LINK)
        ],[
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP_LINK),
            InlineKeyboardButton("🎲 ғᴇᴀᴛᴜʀᴇꜱ 🎲", callback_data="features")
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await cmd.message.edit(
            script.START_TEXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

    elif cb_data.startswith("ban_user_"):
        user_id = cb_data.split("_", 2)[-1]
        if UPDATES_CHANNEL is None:
            await cmd.answer("Sorry Sir, You didn't Set any Updates Channel!", show_alert=True)
            return
        if not int(cmd.from_user.id) == Config.BOT_OWNER:
            await cmd.answer("You are not allowed to do that!", show_alert=True)
            return
        try:
            await bot.kick_chat_member(chat_id=int(UPDATES_CHANNEL), user_id=int(user_id))
            await cmd.answer("User Banned from Updates Channel!", show_alert=True)
        except Exception as e:
            await cmd.answer(f"Can't Ban Him!\n\nError: {e}", show_alert=True)

    elif "genratebatchlink" in cb_data:
        if MediaList.get(f"{str(cmd.from_user.id)}", None) is None:
            MediaList[f"{str(cmd.from_user.id)}"] = []
        file_id = cmd.message.reply_to_message.id
        MediaList[f"{str(cmd.from_user.id)}"].append(file_id)
        message_ids = MediaList.get(f"{str(cmd.from_user.id)}", None)
        if message_ids is None:
            await cmd.answer("Batch List Empty!", show_alert=True)
            return
        await save_batch_media_in_channel(bot=bot, editable=cmd.message, message_ids=message_ids)
        MediaList[f"{str(cmd.from_user.id)}"] = []

    elif "sharable_mode" in cb_data:
        await save_media_in_channel(bot, editable=cmd.message, message=cmd.message.reply_to_message)

    elif "closeMessage" in cb_data:
        await cmd.message.delete(True)
    try:
        await cmd.answer()
    except QueryIdInvalid: pass

Bot.run()
