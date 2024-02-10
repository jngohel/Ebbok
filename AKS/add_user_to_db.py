from info import LOG_CHANNEL, BOT_USERNAME
from AKS.database import db
from pyrogram import Client
from Script import script
from pyrogram.types import Message

async def add_user_to_database(bot: Client, cmd: Message):
    if not await db.is_user_exist(cmd.from_user.id):
        await db.add_user(cmd.from_user.id)
        if LOG_CHANNEL is not None:
            await bot.send_message(LOG_CHANNEL, script.NEW_USER_TEXT.format(cmd.from_user.mention, cmd.from_user.id, @{BOT_USERNAME}))
