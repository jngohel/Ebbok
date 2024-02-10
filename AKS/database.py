import datetime
import motor.motor_asyncio
from info import SHORTENER_WEBSITE, SHORTENER_API, BOT_USERNAME, DATABASE_URL
import requests
import random
import string
import json

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )

    async def generate_random_alphanumeric(self):
        characters = string.ascii_letters + string.digits
        random_chars = ''.join(random.choice(characters) for _ in range(8))
        return random_chars

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def get_shortlink(self, user, link):
        if 'base_site' in user.keys():
            base_site = user["base_site"]
        else:
            base_site = None
        if 'shortener_api' in user.keys():
            api_key = user["shortener_api"]
        else:
            api_key = None
        if not base_site or not api_key:
            base_site = SHORTENER_WEBSITE
            api_key = SHORTENER_API
        gen = await self.generate_random_alphanumeric()
        response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}&alias={gen}")
        data = response.json()
        if data["status"] == "success" or response.status_code == 200:
            return data["shortenedUrl"]

    async def remove_shortener(self, user_id):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        update_value = {"$unset": {"base_site": "", "shortener_api": ""}}
        await self.col.update_one(my_query, update_value)

    async def get_user(self, user_id):
        user_id = int(user_id)
        user = await self.col.find_one({"user_id": user_id})
        if not user:
            res = {
                "user_id": user_id,
                "shortener_api": None,
                "base_site": None
            }
            await self.col.insert_one(res)
            user = await self.col.find_one({"user_id": user_id})
        return user

    async def update_forward_channels(self, user_id, channel_ids):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = {"$set": {"channel_ids": channel_ids}}
        await self.col.update_one(my_query, new_value, upsert=True)

    async def remove_forward_channel(self, user_id, channel_ids):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = {"$pullAll": {"channel_ids": channel_ids}}
        await self.col.update_one(my_query, new_value)

    async def custom_file_caption(self, user_id, caption):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = {"$set": {"caption": caption}}
        await self.col.update_one(my_query, new_value)

    async def remove_caption(self, user_id):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = {"$unset": {"caption": ""}}
        await self.col.update_one(my_query, new_value)
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def update_batch_channel(self, user_id, channel_id):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        if channel_id:
            new_value = {"$set": {"batch_channel": channel_id}}
        else:
            new_value = {"$set": {"batch_channel": ""}}
        await self.col.update_one(my_query, new_value)

    async def remove_batch_channel(self, user_id):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = {"$unset": {"batch_channel": ""}}
        await self.col.update_one(my_query, new_value)

db = Database(DATABASE_URL, BOT_USERNAME)
