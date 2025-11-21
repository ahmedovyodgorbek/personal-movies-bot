from bot.loader import bot
from load_env import GROUP_ID, LOG_GROUP_ID
import asyncio
from aiogram import Bot

from load_env import TOKEN

from celery import shared_task
from aiogram import exceptions
from app.models import TelegramUser
from bot.utils.all import send_log_text
import datetime

@shared_task
def broadcast_ad(ad_chat_id, ad_message_id):
    started_at = datetime.datetime.now()
    users = list(TelegramUser.objects.values_list("telegram_id", flat=True))
    sent = 0
    failed = 0

    async def broadcast():
        nonlocal sent, failed
        # Create a fresh bot instance for this task
        task_bot = Bot(token=TOKEN)
        
        try:
            for user_id in users:
                try:
                    await task_bot.copy_message(
                        chat_id=user_id, 
                        from_chat_id=ad_chat_id, 
                        message_id=ad_message_id
                    )
                    sent += 1
                    await asyncio.sleep(0.05)  # avoid FloodWait
                except Exception:
                    failed += 1
            
            # Send log using the same bot instance
            finished_at = datetime.datetime.now()
            duration = finished_at - started_at
            total_seconds = duration.total_seconds()
            if total_seconds < 1:
                duration_str = f"{total_seconds:.2f}s"
            elif total_seconds < 60:
                duration_str = f"{int(total_seconds)}s"
            else:
                minutes, seconds = divmod(int(total_seconds), 60)
                hours, minutes = divmod(minutes, 60)
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    duration_str = f"{minutes}m {seconds}s"

            await task_bot.send_message(
                chat_id=LOG_GROUP_ID,  # or wherever you send logs
                text=f"✅ Broadcast completed\n\n"
                     f"✅ Sent: {sent}\n"
                     f"❌ Failed: {failed}\n"
                     f"⏱ Duration: {duration_str}"
            )
        finally:
            # Clean up the session
            await task_bot.session.close()

    asyncio.run(broadcast())



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