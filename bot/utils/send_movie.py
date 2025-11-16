from bot.loader import bot
from load_env import GROUP_ID
import asyncio

from celery import shared_task
from aiogram import exceptions



@shared_task
def send_movie_task_async(message_id: int, target_user_id: int):
    """
    Queue async sending of a Telegram movie message.
    Celery runs this synchronously but calls asyncio internally.
    """
    async def _send():
        try:
            await bot.copy_message(
                chat_id=target_user_id,
                from_chat_id=GROUP_ID,
                message_id=message_id,
                protect_content=True
            )
            print(f"✅ Movie {message_id} sent to {target_user_id}")
        except exceptions.TelegramAPIError as e:
            print(f"❌ Telegram error: {str(e)}")

    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_send())