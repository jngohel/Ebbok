from handlers.database import db
from info import BOT_OWNER, 
from handlers.broadcast_handlers import main_broadcast_handler
from pyrogram import Client, enums, filters

MediaList = {}

@Client.on_message(filters.command("set_shortner") & filters.private)
async def set_shortlink(client, message):
    user_id = message.from_user.id
    try:
        _, url, api = message.text.split(" ", 2)
    except ValueError:
        return await message.reply_text("<b>Command Incomplete:-\n\ngive me a shortlink & api along with the command...\n\nEx:- <code>/shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>")   
    user_data = {'base_site': url, 'shortener_api': api}
    await db.update_user_info(user_id, user_data)
    await message.reply_text(f"<b>Successfully set shortlink\n\nURL - {url}\nAPI - <code>{api}</code></b>")

@Client.on_message(filters.command("set_channel") & filters.private)
async def set_channel(client, message):
    user_id = message.from_user.id
    try:
        _, channel_id = message.text.split(" ", 1)
        id = int(channel_id)
        await db.update_forward_channel(user_id, id)      
        await message.reply_text(f"<b>Successfully set channel ID to {id}</b>")
    except ValueError:
        await message.reply_text("<b>Invalid channel ID. Please provide a valid integer.</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Client.on_message(filters.command("remove_channel") & filters.private)
async def remove_channel(client, message):
    user_id = message.from_user.id
    try:
        await db.remove_forward_channel(user_id)
        await message.reply_text("<b>Channel ID removed successfully.</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: <code>{e}</code></b>")

@Client.on_message(filters.private & filters.command("broadcast") & filters.user(BOT_OWNER) & filters.reply)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)

@Client.on_message(filters.private & filters.command("stats") & filters.user(BOT_OWNER))
async def sts(_, m: Message):
    users = await db.total_users_count()
    await m.reply_text(text=f"Total users - <code>`{users}</code></b>")

@Client.on_message(filters.private & filters.command("ban_user") & filters.user(BOT_OWNER))
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

@Client.on_message(filters.private & filters.command("unban_user") & filters.user(BOT_OWNER))
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
      
@Client.on_message(filters.private & filters.command("banned_users") & filters.user(BOT_OWNER))
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

@Client.on_message(filters.private & filters.command("clear_batch"))
async def clear_user_batch(bot: Client, m: Message):
    MediaList[f"{str(m.from_user.id)}"] = []
    await m.reply_text("Cleared your batch files successfully!")
