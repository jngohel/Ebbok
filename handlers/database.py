import datetime
import motor.motor_asyncio
from configs import Config

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

    def generate_random_alphanumeric():
        characters = string.ascii_letters + string.digits
        random_chars = ''.join(random.choice(characters) for _ in range(8))
        return random_chars

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def get_shortlink(user, link):
        base_site = user["url"]
        api_key = user["api"]
        print(user)
        response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}&alias={generate_random_alphanumeric()}")
        data = response.json()
        if data["status"] == "success" or rget.status_code == 200:
            return data["shortenedUrl"]

    async def get_user(self, user_id):
        user_id = int(user_id)
        user = await self.col.find_one({"user_id": user_id})
        if not user:
            res = {
                "user_id": user_id,
                "shortener_api": None,
                "base_site": None,
            }
            await self.col.insert_one(res)
            user = await self.col.find_one({"user_id": user_id})
        return user

    async def update_user_info(self, user_id, value:dict):
        user_id = int(user_id)
        my_query = {"user_id": user_id}
        new_value = { "$set": value }
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

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        return user.get('ban_status', default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({'ban_status.is_banned': True})
        return banned_users

db = Database(Config.DATABASE_URL, Config.BOT_USERNAME)
