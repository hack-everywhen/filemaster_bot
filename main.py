from telethon import TelegramClient
import config_vars
import logging
from database import Database
from handler import Handler
logging.basicConfig(level=logging.WARNING)

bot = TelegramClient(config_vars.BOT_ID, config_vars.API_ID, config_vars.API_HASH)
bot.parse_mode = 'html'
db = Database()
handler = Handler(bot, db)


bot.start(bot_token=config_vars.BOT_TOKEN)
bot.run_until_disconnected()
