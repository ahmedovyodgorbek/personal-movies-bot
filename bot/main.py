import asyncio
import logging
import os
import sys

import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# from load_env import *
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
# from apps.common.middlewares import MembershipCheckMiddleware
from loader import bot, dp


async def main():
    # Middlewares
    # dp.message.middleware(MembershipCheckMiddleware(bot=bot))

    # Add routers to dispatcher
    dp.include_router(router=user_router)
    dp.include_router(router=admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot started polling...")
    logging.basicConfig(level=logging.INFO)
    if __name__ == "__main__":
        print("Welcome to Movies Bot")
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            print("Bot stopped!")

