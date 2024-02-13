import os

API_ID = int(os.environ.get("API_ID", "24998279"))
API_HASH = os.environ.get("API_HASH", "b2ec3ab8ed156e7a6782f3d7d1acbaf6")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6746873232:AAFQ9JvDDNLS6EaJeIc2kSzeYDHAa3uLEGY")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Raj_Auto_bot")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1001969537424"))
SHORTENER_WEBSITE = os.environ.get('SHORTENER_WEBSITE', "ziplinker.net")
SHORTENER_API = os.environ.get('SHORTENER_API', "9d0bf6423069cbf46c75a985e270e5ddfb537f0f")
ADMINS = int(os.environ.get("ADMINS", "866072531"))
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://Jng:jng@cluster0.vvrnobg.mongodb.net/?retryWrites=true&w=majority")
AUTH_CHANNEL = os.environ.get("AUTH_CHANNEL", "-1001873197309")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001849681109"))
FORWARD_AS_COPY = bool(os.environ.get("FORWARD_AS_COPY", False))
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))
BANNED_CHAT_IDS = list(set(int(x) for x in os.environ.get("BANNED_CHAT_IDS", "").split()))
OTHER_USERS_CAN_SAVE_FILE = bool(os.environ.get("OTHER_USERS_CAN_SAVE_FILE", True))
DELETE_TIME = int(os.environ.get('DELETE_TIME', 1200))

#for stream
BIN_CHANNEL = int(os.environ.get('BIN_CHANNEL', '-1001696019751'))
URL = os.environ.get('URL', 'aks-file-to-link-525cd78edc50.herokuapp.com')

#this vars for start message button
SUPPORT_GROUP_LINK = os.environ.get("SUPPORT_GROUP_LINK", "https://t.me/FilmyFundas")
UPDATES_CHANNEL_LINK = os.environ.get("UPDATES_CHANNEL_LINK", "https://t.me/FilmyFundas")
