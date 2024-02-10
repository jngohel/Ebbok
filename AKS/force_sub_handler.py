import asyncio
from typing import Union
from info import AUTH_CHANNEL
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

async def get_invite_link(bot: Client, chat_id: Union[str, int]):
    try:
        invite_link = await bot.create_chat_invite_link(chat_id=chat_id)
        return invite_link
    except FloodWait as e:
        print(f"Sleep of {e.value}s caused by FloodWait ...")
        await asyncio.sleep(e.value)
        return await get_invite_link(bot, chat_id)

async def handle_force_sub(bot: Client, cmd: Message):
    if AUTH_CHANNEL and AUTH_CHANNEL.startswith("-100"):
        channel_chat_id = int(AUTH_CHANNEL)
    elif AUTH_CHANNEL and (not AUTH_CHANNEL.startswith("-100")):
        channel_chat_id = AUTH_CHANNEL
    else:
        return 200
    try:
        user = await bot.get_chat_member(chat_id=channel_chat_id, user_id=cmd.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text="Sorry Sir, You are Banned to use me",
                disable_web_page_preview=True
            )
            return 400
    except UserNotParticipant:
        try:
            invite_link = await get_invite_link(bot, chat_id=channel_chat_id)
        except Exception as err:
            print(f"Unable to do Force Subscribe to {AUTH_CHANNEL}\n\nError: {err}")
            return 200
        btn = [
            [InlineKeyboardButton("🚫 ᴊᴏɪɴ ɴᴏᴡ 🚫", url=invite_link.invite_link)],
            [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data="checksub")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="<b><i>🙁 ғɪʀꜱᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴍᴏᴠɪᴇ, ᴏᴛʜᴇʀᴡɪꜱᴇ ʏᴏᴜ ᴡɪʟʟ ɴᴏᴛ ɢᴇᴛ ɪᴛ.\n\nᴄʟɪᴄᴋ ᴊᴏɪɴ ɴᴏᴡ ʙᴜᴛᴛᴏɴ 👇</i></b>",
            reply_markup=reply_markup
        )
        return 400
    except Exception as e:
        print(e)
        return 200
    return 200
