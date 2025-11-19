from asgiref.sync import sync_to_async
from movies.models import Movies
from aiogram.types import Message
from app.models import TelegramUser

async def is_subscribed(bot, user_id: int, channel_id: str | int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)

        # Possible statuses: "creator", "administrator", "member", "restricted", "left", "kicked"
        return member.status in ("creator", "administrator", "member")

    except Exception:
        # Bot was removed from the channel OR invalid channel ID
        return False


def mention_user(user_id: int, first_name: str) -> str:
    from html import escape
    safe_name = escape(first_name or "Unknown")
    return f"<a href='tg://user?id={user_id}'>{safe_name}</a>"


async def post_text(movie:Movies):
    genres = await sync_to_async(list)(movie.genres.all())
    genres = [f"#{genre}" for genre in genres]
    genres_text = " ".join(genres)
    text = (
        f"<b>{movie.type.capitalize()}: {movie.title}</b>\n"
        f"<b>ID: {movie.id}</b>\n\n"
        f"  <b>- Genre:</b> {genres_text}\n"
        f"  <b>- Year:</b> {movie.release_date}\n"
        f"  <b>- IMDb:</b> {movie.rating}/10\n"
        f"  <b>- Cast:</b> {movie.actors}\n\n"
        f"Send the ID  to the bot\n"
        f"Bot - @AhmedovMoviesBot"
    )
    return text


@sync_to_async
def create_or_update_user(message:Message):
    is_premium = getattr(message.from_user, "is_premium", False) or False

    user, created = TelegramUser.objects.update_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language_code": message.from_user.language_code,
            "is_premium": is_premium
        }
    )
    return user


def handle_user_referral(message: Message, args: str):
    referrer = None

    if args.startswith("ref_"):
        ref_code = args.replace("ref_", "")
        try:
            referrer = TelegramUser.objects.get(referral_code=ref_code)
            # 🔒 Prevent self-referral
            if referrer.telegram_id == message.from_user.id:
                referrer = None
        except TelegramUser.DoesNotExist:
            referrer = None

    is_premium = getattr(message.from_user, "is_premium", False) or False

    user, created = TelegramUser.objects.update_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language_code": message.from_user.language_code,
            "is_premium": is_premium,
            
        }
    )
    if created and referrer:
        user.referrer = referrer
        user.save(update_fields=["referrer"])

    return user, created, referrer


from django.db.models import Count
from asgiref.sync import sync_to_async

async def get_user_rank(telegram_id: int) -> tuple:
    # Annotate users with number of referrals, order descending
    users = await sync_to_async(
        lambda: list(
            TelegramUser.objects.annotate(num_referrals=Count('referrals'))
            .order_by('-num_referrals')
            .values('telegram_id', 'num_referrals')
        )
    )()

    # Find the user’s position
    for index, u in enumerate(users, start=1):
        if u['telegram_id'] == telegram_id:
            return index, u['num_referrals']  # rank, referral count
    
    return None, 0  # user not found