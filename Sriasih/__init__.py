import asyncio
import time
from inspect import getfullargspec
from os import path
from geezlibs import DEVS
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from pyrogram import Client
from pyrogram.types import Message
from pyromod import listen
from Python_ARQ import ARQ
from telegraph import Telegraph
from os import environ, path

from dotenv import load_dotenv

if path.exists("config.env"):
    load_dotenv("config.env")
    
    
BOT_TOKEN = environ.get("BOT_TOKEN", None)
API_ID = int(environ.get("API_ID", 6))
API_HASH = environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
SUDO_USERS_ID = [int(x) for x in environ.get("SUDO_USERS_ID", "").split()]
LOG_GROUP_ID = int(environ.get("LOG_GROUP_ID", None))
GBAN_LOG_GROUP_ID = int(environ.get("GBAN_LOG_GROUP_ID", None))
MESSAGE_DUMP_CHAT = int(environ.get("MESSAGE_DUMP_CHAT", None))
WELCOME_DELAY_KICK_SEC = int(environ.get("WELCOME_DELAY_KICK_SEC", None))
MONGO_URL = environ.get("MONGO_URL", None)
ARQ_API_URL = environ.get("ARQ_API_URL", None)
ARQ_API_KEY = environ.get("ARQ_API_KEY", None)
RSS_DELAY = int(environ.get("RSS_DELAY", None))
STRING_SESSION = environ.get("STRING_SESSION")
BLACKLIST_CHAT = environ.get("BLACKLIST_CHAT")
UPSTREAM_REPO = environ.get(
    "UPSTREAM_REPO", ""
)


ALIVE_LOGO = "https://telegra.ph/file/5d71546548f5a2e3a896e.png"
GBAN_LOG_GROUP_ID = GBAN_LOG_GROUP_ID
SUDOERS = DEVS
WELCOME_DELAY_KICK_SEC = WELCOME_DELAY_KICK_SEC
LOG_GROUP_ID = LOG_GROUP_ID
MESSAGE_DUMP_CHAT = MESSAGE_DUMP_CHAT
MOD_LOAD = []
MOD_NOLOAD = []
bot_start_time = time.time()

# MongoDB client
print("[INFO]: INITIALIZING DATABASE")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.pitung


async def load_sudoers():
    global SUDOERS
    print("[INFO]: LOADING SUDOERS")
    sudoersdb = db.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    for user_id in SUDOERS:
        if user_id not in sudoers:
            sudoers.append(user_id)
            await sudoersdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"sudoers": sudoers}},
                upsert=True,
            )
    SUDOERS = (SUDOERS + sudoers) if sudoers else SUDOERS
    print("[INFO]: LOADED SUDOERS")


loop = asyncio.get_event_loop()
loop.run_until_complete(load_sudoers())

aiohttpsession = ClientSession()

arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

app = Client("sipitung", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

print("[INFO]: STARTING BOT CLIENT")
app.start()

print("[INFO]: GATHERING PROFILE INFO")
x = app.get_me()

bot1 = (
    Client(
        name="bot1",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
    )
    if STRING_SESSION
    else None
)
print("[INFO]: STARTING ASSISTANT")
bot1.start()
y = bot1.get_me

BOT_ID = x.id
BOT_NAME = x.first_name + (x.last_name or "")
ASST_NAME = y.first_name + (y.last_name or "")
BOT_USERNAME = x.username
ASST_USERNAME = y.username
BOT_MENTION = x.mention
ASST_MENTION = y.mention
BOT_DC_ID = x.dc_id

telegraph = Telegraph()
telegraph.create_account(short_name=BOT_USERNAME)


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})
