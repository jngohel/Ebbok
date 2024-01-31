import os
import asyncio
import traceback
from binascii import Error
from Script import script
from pyrogram import Client, enums, filters
from pyrogram.errors import UserNotParticipant, FloodWait, QueryIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from info import DB_CHANNEL, AUTH_CHANNEL, BANNED_USERS, API_HASH, API_ID, BOT_USERNAME, BOT_TOKEN, LOG_CHANNEL, OTHER_USERS_CAN_SAVE_FILE, BOT_OWNER, BANNED_CHAT_IDS, SUPPORT_GROUP_LINK, UPDATES_CHANNEL_LINK, SHORTENER_WEBSITE, SHORTENER_API
from handlers.database import db
from handlers.add_user_to_db import add_user_to_database
from handlers.send_file import send_media_and_reply
from handlers.helpers import b64_to_str, str_to_b64
from handlers.check_user_status import handle_user_status
from handlers.force_sub_handler import handle_force_sub, get_invite_link
from handlers.broadcast_handlers import main_broadcast_handler
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

@Bot.on_message(filters.command("set_caption") & filters.private)
async def set_caption(client, message):
    user_id = message.from_user.id
    try:
        caption = (message.text).split(" ", 1)[1]
    except IndexError:
        return await message.reply_text("<b>ɢɪᴠᴇ ᴍᴇ ᴀ ᴄᴀᴘᴛɪᴏɴ ᴀʟᴏɴɢ ᴡɪᴛʜ ɪᴛ.\n\nᴇxᴀᴍᴘʟᴇ -\n\nꜰᴏʀ ꜰɪʟᴇ ᴅᴜʀᴀᴛɪᴏɴ ꜱᴇɴᴅ <code>{duration}</code>\nꜰᴏʀ ꜰɪʟᴇ ɴᴀᴍᴇ ꜱᴇɴᴅ <code>{file_name}</code>\nꜰᴏʀ ꜰɪʟᴇ ꜱɪᴢᴇ ꜱᴇɴᴅ <code>{file_size}</code>\n\n<code>/set_caption {file_name}</code></b>")
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

@Bot.on_message(filters.command("remove_shortener") & filters.private)
async def remove_shortener(client, message):
    user_id = message.from_user.id
    try:
        await db.update_user_info(user_id, {'base_site': SHORTENER_WEBSITE, 'shortener_api': SHORTENER_API})
        await message.reply_text("<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʏᴏᴜʀ ꜱʜᴏʀᴛᴇɴᴇʀ ʀᴇᴍᴏᴠᴇᴅ ᴀɴᴅ ᴀᴅᴅᴇᴅ ᴅᴇꜰᴀᴜʟᴛ ᴅᴀᴛᴀ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("set_channel") & filters.private)
async def set_channel(client, message):
    user_id = message.from_user.id
    try:
        _, channel_id = message.text.split(" ", 1)
        id = int(channel_id)
        await db.update_forward_channel(user_id, id)      
        await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ ɪᴅ\n\n<code>{id}</code></b>")
    except ValueError:
        await message.reply_text("<b>ꜱᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴡɪᴛʜ ᴄᴏᴍᴍᴀɴᴅ\n\n⚠️ ɴᴏᴛᴇ - ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Bot.on_message(filters.command("remove_channel") & filters.private)
async def remove_channel(client, message):
    user_id = message.from_user.id
    try:
        await db.remove_forward_channel(user_id)
        await message.reply_text("<b>ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ ɪᴅ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅️</b>")
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
        text = f"""ꜱʜᴏʀᴛᴇɴᴇʀ - `{user['base_site']}`
ᴀᴘɪ - `{user['shortener_api']}`

ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ - `{user.get('channel_id')}`

ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - `{user.get('caption')}`"""
        await message.reply_text(text, reply_markup=reply_markup)
 
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

@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(BOT_OWNER) & filters.reply)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)

@Bot.on_message(filters.private & filters.command("stats") & filters.user(BOT_OWNER))
async def sts(_, m: Message):
    users = await db.total_users_count()
    await m.reply_text(text=f"Total users - <code>`{users}</code></b>")

@Bot.on_message(filters.private & filters.command("ban_user") & filters.user(BOT_OWNER))
async def ban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban any user from the bot.\n\n"
            f"Usage:\n\n"
            f"`/ban_user user_id ban_duration ban_reason`\n\n"
            f"Eg: `/ban_user 1234567 28 You misused me.`\n"
            f"This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True
        )
        return
    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )

@Bot.on_message(filters.private & filters.command("unban_user") & filters.user(BOT_OWNER))
async def unban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban any user.\n\n"
            f"Usage:\n\n`/unban_user user_id`\n\n"
            f"Eg: `/unban_user 1234567`\n"
            f"This will unban user with id `1234567`.",
            quote=True
        )
        return
    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"
        try:
            await c.send_message(
                user_id,
                f"Your ban was lifted!"
            )
            unban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occurred! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )

@Bot.on_message(filters.private & filters.command("banned_users") & filters.user(BOT_OWNER))
async def _banned_users(_, m: Message):    
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ''
    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, " \
                f"**Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('banned-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('banned-users.txt')
        return
    await m.reply_text(reply_text, True)

@Bot.on_message(filters.private & filters.command("clear_batch"))
async def clear_user_batch(bot: Client, m: Message):
    MediaList[f"{str(m.from_user.id)}"] = []
    await m.reply_text("Cleared your batch files successfully!")

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
        if AUTH_CHANNEL is None:
            await cmd.answer("Sorry Sir, You didn't Set any Updates Channel!", show_alert=True)
            return
        if not int(cmd.from_user.id) == BOT_OWNER:
            await cmd.answer("You are not allowed to do that!", show_alert=True)
            return
        try:
            await bot.kick_chat_member(chat_id=int(AUTH_CHANNEL), user_id=int(user_id))
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

    elif "close_data" in cb_data:
        await cmd.message.delete(True)
    try:
        await cmd.answer()
    except QueryIdInvalid: pass

Bot.run()
