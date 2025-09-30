import asyncio
import logging
import os
import sys

import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# from load_env import *
# from apps.start.handlers import StartHandler
# from apps.common.middlewares import MembershipCheckMiddleware
from loader import bot, dp


async def main():
    # Middlewares
    # dp.message.middleware(MembershipCheckMiddleware(bot=bot))

    # Initialize handlers (registers routes to routers)
    # start_handler = StartHandler()

    # Add routers to dispatcher
    # dp.include_router(router=start_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
