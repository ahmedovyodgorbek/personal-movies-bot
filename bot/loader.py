from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from load_env import TOKEN

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())