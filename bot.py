import os
import asyncio
import traceback
from binascii import Error
from Script import script
from pyrogram import Client, enums, filters
from pyrogram.errors import UserNotParticipant, FloodWait, QueryIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from info import DB_CHANNEL, AUTH_CHANNEL, API_HASH, API_ID, BOT_USERNAME, BOT_TOKEN, LOG_CHANNEL, OTHER_USERS_CAN_SAVE_FILE, ADMINS, BANNED_CHAT_IDS, SUPPORT_GROUP_LINK, UPDATES_CHANNEL_LINK, SHORTENER_WEBSITE, SHORTENER_API, DELETE_TIME
from AKS.database import db
from AKS.add_user_to_db import add_user_to_database, handle_user_status
from AKS.send_file import send_media_and_reply, reply_forward, delete_after_delay
from AKS.helpers import b64_to_str, str_to_b64, get_readable_time
from AKS.force_sub_handler import handle_force_sub, get_invite_link
from AKS.broadcast import users_broadcast
from AKS.save_media import save_media_in_channel, save_batch_in_channel

MediaList = {}

Bot = Client(
    name=BOT_USERNAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

@Bot.on_message(filters.private)
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

@Bot.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):
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
                    text=f"<b>📝 ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ - <code>{len(message_ids)}</code></b>",
                    quote=True,
                    disable_web_page_preview=True
                )
            else:
                message_ids.append(int(GetMessage.id))
            for i in range(len(message_ids)):
                await send_media_and_reply(bot, user_id=cmd.from_user.id, file_id=int(message_ids[i]), uniqStr=(usr_cmd.split("_")[-1]))
            await reply_forward(bot, cmd.from_user.id)
            await delete_after_delay(uniqStr=(usr_cmd.split("_")[-1]), delay=DELETE_TIME)
        except Exception as e:
            print(e)

@Bot.on_message((filters.document | filters.video) & ~filters.chat(DB_CHANNEL))
async def main(bot: Client, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        await add_user_to_database(bot, message)
        if AUTH_CHANNEL is not None:
            back = await handle_force_sub(bot, message)
            if back == 400:
                return
        if OTHER_USERS_CAN_SAVE_FILE is False:
            return
        if message.document and message.document.thumbs[0]:
            thumb = message.document.thumbs[0]
        elif message.video and message.video.thumbs[0]:
            thumb = message.video.thumbs[0]
        elif message.audio and message.audio.thumbs[0]:
            thumb = message.audio.thumbs[0]
        else:
            thumb = None
        if thumb is None:
            editTXT = await message.reply_photo(
                photo="https://icon-library.com/images/png-file-icon/png-file-icon-6.jpg",
                caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>",
                quote=True,
                parse_mode=enums.ParseMode.HTML
            )
            await save_media_in_channel(bot, editTXT, message)
        else:
            thumb_jpg = await bot.download_media(thumb) #download thumb to current working dir
            editTXT = await message.reply_photo(
                photo=thumb_jpg,
                caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>",
                quote=True,
                parse_mode=enums.ParseMode.HTML
            )
            await save_media_in_channel(bot, editTXT, message)
            os.remove(thumb_jpg)
    elif message.chat.type == enums.ChatType.CHANNEL:
        if (message.chat.id == int(LOG_CHANNEL)) or (message.chat.id == int(AUTH_CHANNEL)) or message.forward_from_chat or message.forward_from:
            return
        elif int(message.chat.id) in BANNED_CHAT_IDS:
            await bot.leave_chat(message.chat.id)
            return
        else:
            pass        

@Bot.on_message(filters.command("batch") & filters.private)
async def addBatch(bot: Client, message: Message):
    cmd_txt = message.text
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    batch = user.get("batch_channel")
    if not batch:
        return await message.reply_text("<b>‼️ꜰɪʀꜱᴛ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ꜱᴇᴛ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ ꜱᴛᴏʀᴇ ʏᴏᴜʀ ʙᴀᴛᴄʜ ꜰɪʟᴇꜱ.\n\nꜱᴇᴛ ᴜꜱɪɴɢ ᴛʜɪꜱ - <code>/set_batch_channel -100********</code>\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ</b>")
    try:
        link1 = int(((cmd_txt.split(" ", 3)[1]).split("t.me/c/", 2)[1]).split('/', 2)[1])
        link2 = int(((cmd_txt.split(" ", 3)[2]).split("t.me/c/", 2)[1]).split('/', 2)[1])
        linksList = [link1, link2]
    except IndexError:
        return await message.reply_text(text="<b>ᴜꜱᴇ ᴘʀᴏᴘᴇʀ ꜰᴏʀᴍᴀᴛ ʟɪᴋᴇ\n\n<code>/batch ᴘᴏꜱᴛʟɪɴᴋ1 ᴘᴏꜱᴛʟɪɴᴋ2</code></b>", quote=True)
    else:
        temp_msg1 = await bot.get_messages(chat_id=batch, message_ids=link1)
        if temp_msg1.document and temp_msg1.document.thumbs[0]:
            thumb = temp_msg1.document.thumbs[0]
        elif temp_msg1.video and temp_msg1.video.thumbs[0]:
            thumb = temp_msg1.video.thumbs[0]
        elif temp_msg1.audio and temp_msg1.audio.thumbs[0]:
            thumb = temp_msg1.audio.thumbs[0]
        else:
            thumb = None
        if thumb is None:
            reply_msg = await message.reply_photo(
                photo="https://icon-library.com/images/png-file-icon/png-file-icon-6.jpg",
                caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>", 
                quote=True
            )
        else:
            thumb_jpg = await bot.download_media(thumb)
            reply_msg = await message.reply_photo(
                photo=thumb_jpg,
                caption="<b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</b>",
                quote=True,
                parse_mode=enums.ParseMode.HTML
            )
            os.remove(thumb_jpg)
        await save_batch_in_channel(bot, message, reply_msg, linksList)

@Bot.on_message(filters.command("set_caption") & filters.private)
async def set_caption(client, message):
    user_id = message.from_user.id
    try:
        caption = (message.text).split(" ", 1)[1]
    except IndexError:
        return await message.reply_text("<b>ɢɪᴠᴇ ᴍᴇ ᴀ ᴄᴀᴘᴛɪᴏɴ ᴀʟᴏɴɢ ᴡɪᴛʜ ɪᴛ.\n\nᴇxᴀᴍᴘʟᴇ -\n\nꜰᴏʀ ꜰɪʟᴇ ᴅᴜʀᴀᴛɪᴏɴ <code>{duration}</code>\nꜰᴏʀ ꜰɪʟᴇ ɴᴀᴍᴇ <code>{file_name}</code>\nꜰᴏʀ ꜰɪʟᴇ ꜱɪᴢᴇ <code>{file_size}</code>\nꜰᴏʀ ꜱʜᴏʀᴛʟɪɴᴋ <code>{short_link}</code>\n\n<code>/set_caption {file_name}</code></b>")
    else:
        await db.custom_file_caption(user_id, caption)
        return await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʏᴏᴜʀ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ\n\n<code>{caption}</code></b>")

@Bot.on_message(filters.command("remove_caption") & filters.private)
async def remove_caption(client, message):
    user_id = message.from_user.id
    try:
        await db.remove_caption(user_id)
        await message.reply_text("<b>ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ, ɴᴏᴡ ᴏɴʟʏ ꜰɪʟᴇ ɴᴀᴍᴇ ꜱʜᴏᴡ.</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("set_shortner") & filters.private)
async def set_shortlink(client, message):
    user_id = message.from_user.id
    try:
        _, url, api = message.text.split(" ", 2)
    except ValueError:
        return await message.reply_text("<b>ꜱᴇɴᴅ ᴍᴇ ꜱʜᴏʀᴛʟɪɴᴋ ᴀɴᴅ ᴀᴘɪ ᴡɪᴛʜ ᴄᴏᴍᴍᴀɴᴅ\n\nᴇx - <code>/set_shortner tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354</code></b>")   
    user_data = {'base_site': url, 'shortener_api': api}
    await db.update_user_info(user_id, user_data)
    await message.reply_text(f"<b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʏᴏᴜʀ ꜱʜᴏʀᴛʟɪɴᴋ\n\nꜱʜᴏʀᴛʟɪɴᴋ - {url}\nᴀᴘɪ - `{api}`</b>")

@Bot.on_message(filters.command("remove_shortner") & filters.private)
async def remove_shortener(client, message):
    user_id = message.from_user.id
    try:
        await db.remove_shortener(user_id)
        await message.reply_text("<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʏᴏᴜʀ ꜱʜᴏʀᴛᴇɴᴇʀ ʀᴇᴍᴏᴠᴇᴅ ᴀɴᴅ ᴀᴅᴅᴇᴅ ᴅᴇꜰᴀᴜʟᴛ ᴅᴀᴛᴀ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("set_channel") & filters.private)
async def set_channel(client, message):
    user_id = message.from_user.id
    try:
        _, *channel_ids = message.text.split(" ")
        ids = [int(channel_id) for channel_id in channel_ids]
        for channel_id in ids:
            try:
                chat = await client.get_chat(channel_id)
            except Exception as e:
                return await message.reply_text(f"<b><code>{channel_id}</code> ɪɴᴠᴀʟɪᴅ!!\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ\n\nError - {e}</b>")
        await db.update_forward_channels(user_id, ids)      
        await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ ɪᴅ\n\n<code>{', '.join(map(str, ids))}</code></b>")
    except ValueError:
        await message.reply_text("<b>ꜱᴇɴᴅ ᴍᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ꜱᴇᴘᴀʀᴀᴛᴇᴅ ʙʏ ᴛʜᴇ ꜱᴘᴀᴄᴇ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.\n\nᴇx - <code>/set_channel -100******** -100*******</code>\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("remove_channel") & filters.private)
async def remove_channel(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get('channel_ids'):
        await message.reply_text("<b>⚠️ ɴᴏ ᴀɴʏ ᴄʜᴀɴɴᴇʟ ɪᴅ ꜰᴏᴜɴᴅ</b>")
        return
    try:
        _, *channel_ids = message.text.split(" ")
        if not channel_ids:
            await message.reply_text("<b>⚠️ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ</b>")
            return
        ids = [int(channel_id) for channel_id in channel_ids]
        await db.remove_forward_channel(user_id, ids)
        await message.reply_text("<b>ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ ɪᴅ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅️</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("set_batch_channel") & filters.private)
async def set_batch_channel(client, message):
    user_id = message.from_user.id
    try:
        _, channel_id = message.text.split(" ", 1)
        channel_id = int(channel_id)
        try:
            chat = await client.get_chat(channel_id)
        except Exception as e:
            return await message.reply_text(f"<b><code>{channel_id}</code> ɪɴᴠᴀʟɪᴅ!!\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ\n\nError - {e}</b>")
        await db.update_batch_channel(user_id, channel_id)
        await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ ɪᴅ\n\n<code>{channel_id}</code></b>")
    except ValueError:
        await message.reply_text("<b>ꜱᴇɴᴅ ᴍᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴡɪᴛʜ ᴄᴏᴍᴍᴀɴᴅ ʟɪᴋᴇ\n\n<code>/set_batch_channel -100*********</code>\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("remove_batch_channel") & filters.private)
async def remove_batch_channel(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get('batch_channel'):
        await message.reply_text("<b>⚠️ ɴᴏ ᴀɴʏ ᴄʜᴀɴɴᴇʟ ɪᴅ ꜰᴏᴜɴᴅ</b>")
        return
    try:
        await db.remove_batch_channel(user_id)
        await message.reply_text("<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ ɪᴅ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command('info') & filters.private)
async def info(client, message):
    btn = [[
        InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close_data")
    ]]
    reply_markup=InlineKeyboardMarkup(btn)
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if user:
        base_site = user.get('base_site', SHORTENER_WEBSITE)
        api_key = user.get('shortener_api', SHORTENER_API)
        if base_site == SHORTENER_WEBSITE:
            web = base_site + "[ᴅᴇꜰᴀᴜʟᴛ]"
        else:
            web = base_site
        if api_key == SHORTENER_API:
            api = api_key + "[ᴅᴇꜰᴀᴜʟᴛ]"
        else:
            api = api_key
        batch_channel = user.get('batch_channel')
        if batch_channel:
            batch = str(batch_channel)
        else:
            batch = "ɴᴏᴛ ꜱᴇᴛ"
        target_channel = user.get('channel_ids')
        if target_channel:
            target = ', '.join(map(str, target_channel))
        else:
            target = "ɴᴏᴛ ꜱᴇᴛ"
        cap = user.get('caption')
        if cap:
            caption = user.get('caption')
        else:
            caption = "ɴᴏᴛ ꜱᴇᴛ"
        text = f"""<b>📊 ꜱʜᴏʀᴛᴇɴᴇʀ - `{web}`
        
‼️ ᴀᴘɪ - `{api}`

♻️ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ - `{target}`

📥 ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ - `{batch}`

📝 ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - `{caption}`</b>"""
        await message.reply_text(text, reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(_, m: Message):
    await users_broadcast(m, db)

@Bot.on_message(filters.private & filters.command("stats") & filters.user(ADMINS))
async def sts(_, m: Message):
    users = await db.total_users_count()
    await m.reply_text(text=f"<b>🤖 ᴛᴏᴛᴀʟ ᴜꜱᴇʀ - `{users}</b>")

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
            except UserNotParticipant:
                invite_link = await get_invite_link(bot, chat_id=channel_chat_id)
                await cmd.answer("😶 ɪ ʟɪᴋᴇ ʏᴏᴜʀ ꜱᴍᴀʀᴛɴᴇꜱꜱ ʙᴜᴛ ᴅᴏɴ'ᴛ ʙᴇ ᴏᴠᴇʀꜱᴍᴀʀᴛ!", show_alert=True)
                return
            except Exception:
                await cmd.message.edit(
                    text="Something went Wrong.",
                    disable_web_page_preview=True
                )
                return
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
    
    elif "close_data" in cb_data:
        await cmd.message.delete(True)
    try:
        await cmd.answer()
    except QueryIdInvalid: pass

Bot.run()
