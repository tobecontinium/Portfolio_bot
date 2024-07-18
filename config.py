from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from environs import Env

env = Env()
env.read_env()

API_TOKEN = env('BOT_TOKEN')
ADMIN_ID = env('ADMIN_ID')
CHANNEL_ID = env('CHANNE_ID')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())