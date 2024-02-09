import os

API_ID = int(os.environ.get("API_ID", "12197477"))
API_HASH = os.environ.get("API_HASH", "ac077d8acc256685720b14eba02d8d11")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6144777379:AAHYgccuRRZRn-TT3_zBld4yQREDidoVke8")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "aks_file_store_bot")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1001768689210"))
SHORTENER_WEBSITE = os.environ.get('SHORTENER_WEBSITE', "mdiskshortner.link")
SHORTENER_API = os.environ.get('SHORTENER_API', "e7beb3c8f756dfa15d0bec495abc65f58c0dfa95")
ADMINS = int(os.environ.get("ADMINS", "1030335104"))
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://ttttechnicalaks7:filestorebotclone@cluster0.ch7domc.mongodb.net/?retryWrites=true&w=majority")
AUTH_CHANNEL = os.environ.get("AUTH_CHANNEL", "-1001831955243")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001769642119"))
FORWARD_AS_COPY = bool(os.environ.get("FORWARD_AS_COPY", False))
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))
BANNED_CHAT_IDS = list(set(int(x) for x in os.environ.get("BANNED_CHAT_IDS", "").split()))
OTHER_USERS_CAN_SAVE_FILE = bool(os.environ.get("OTHER_USERS_CAN_SAVE_FILE", True))
BATCH_CHANNEL = int(os.environ.get("BATCH_CHANNEL", "-1002120917360"))
DELETE_TIME = int(os.environ.get('DELETE_TIME', 1200))
URL = os.environ.get('URL', 'aks-file-to-link-525cd78edc50.herokuapp.com')

#this vars for start message button
SUPPORT_GROUP_LINK = os.environ.get("SUPPORT_GROUP_LINK", "https://t.me/aks_bot_support")
UPDATES_CHANNEL_LINK = os.environ.get("UPDATES_CHANNEL_LINK", "https://t.me/Imdb_updates")
