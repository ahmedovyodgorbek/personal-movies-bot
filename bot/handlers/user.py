from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from asgiref.sync import sync_to_async
from django.db import transaction
from app.models import TelegramUser
from django.db.models import Count
from bot.keyboards.user import admin
from html import escape
from django.utils import timezone



router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, command: CommandObject):
    args = command.args or ""

    # Run DB logic in a synchronous thread
    user, created, referrer = await sync_to_async(handle_user_referral)(message, args)

    # --- Messaging logic ---
    if created:
        text = "👋 Welcome to the bot!"
        if referrer:
            text += f"\n🎉 You were invited by @{referrer.username or referrer.telegram_id}."
            try:
                safe_name = escape(user.first_name or "Unknown")
                if user.username:
                    name = f"@{user.username}" 
                else:
                    name = f"<a href='tg://user?id={message.from_user.id}'>{safe_name}</a>"
                await message.bot.send_message(
                    referrer.telegram_id,
                    f"🎊 Your friend {name} just joined using your referral link!"
                )
            except Exception:
                pass
    else:
        text = "👋 Welcome back!"

    await message.answer(text)


@router.message(Command("friends"))
async def friends(message: Message):
    user = await create_or_update_user(message)
    top_users = await sync_to_async(
        lambda: list(
            TelegramUser.objects.annotate(num_referrals=Count('referrals'))
            .order_by('-num_referrals')
            .values('telegram_id', 'num_referrals', 'username', 'first_name')[:10]
        )
    )()
    friends_count = 0
    if user:
        ranking, friends_count = await get_user_rank(telegram_id=user.telegram_id)

    text = (
        f"🎯 <b>Your Stats:</b>\n"
        f"👥 Friends: <b>{friends_count}</b>\n"
        f"🏆 Your Rank: <b>#{ranking}</b>\n\n"
    )

    # Top users leaderboard
    if top_users:
        text += "🌟 <b>Top Referrers:</b>\n"
        for index, user in enumerate(top_users, start=1):
            # Choose display name safely
            first_name = escape(user['first_name'] or "Unknown")
            user_id = int(user['telegram_id'])
            name = mention_user(user['telegram_id'], user['first_name'])
            # Add trophy emojis for top 3
            if index == 1:
                medal = "🥇"
            elif index == 2:
                medal = "🥈"
            elif index == 3:
                medal = "🥉"
            else:
                medal = "🔹"
            text += f"{medal} {index}. {name} — {user['num_referrals']} friends\n"

    # Send message with HTML parse mode
    await message.answer(text=text, parse_mode="HTML")
    
def mention_user(user_id: int, first_name: str) -> str:
    from html import escape
    safe_name = escape(first_name or "Unknown")
    return f"<a href='tg://user?id={user_id}'>{safe_name}</a>"

@router.message(Command("admin"))
async def contact_admin(message: Message):
    user = await create_or_update_user(message)
    await message.answer(text="Click on the button to contact with Admin", reply_markup=admin())

@router.message(Command("referral"))
async def invite_friends(message: Message, command: CommandObject):
    user = await create_or_update_user(message)
    text = (f"Share this link: \n\n" 
            f"<b>{user.referral_link}</b>\n\n"
            f"Climb the leaderboard and get more referrals! 🥇🥈🥉")
    
    await message.answer(text=text, parse_mode="HTML")


@sync_to_async
def create_or_update_user(message:Message):
    is_premium = getattr(message.from_user, "is_premium", False) or False

    now = timezone.now()
    user, created = TelegramUser.objects.update_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language_code": message.from_user.language_code,
            "is_premium": is_premium,
            "last_activity": now
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