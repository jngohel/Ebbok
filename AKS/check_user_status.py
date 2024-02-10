import datetime
from Script import script
from info import BOT_USERNAME, DATABASE_URL, LOG_CHANNEL
from AKS.database import Database

db = Database(DATABASE_URL, BOT_USERNAME)

async def handle_user_status(bot, cmd):
    chat_id = cmd.from_user.id
    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        await bot.send_message(LOG_CHANNEL, text=script.NEW_USERS_TEXT.format(cmd.from_user.mention, cmd.from_user.id, {BOT_USERNAME}))
    await cmd.continue_propagation()
            
