from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from asgiref.sync import sync_to_async
from django.db import transaction
from app.models import TelegramUser
from django.db.models import Count
from bot.keyboards.user import admin, channels_keyboard
from bot.keyboards.admin import admin_menu
from html import escape
from bot.utils.all import *

import load_env

from movies.models import Movies, PartnerChannels

router = Router()

@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def start_handler(message: Message, command: CommandObject):
    if str(message.from_user.id) in load_env.ADMINS:
        await message.answer(text="Welcome to Admin Menu", reply_markup=admin_menu())
        return
    
    args = command.args or ""

    # Run DB logic in a synchronous thread
    user, created, referrer = await sync_to_async(handle_user_referral)(message, args)

    # --- Messaging logic ---
    if created:
        text = (f"👤 New User has started the bot✅\n\n"
                f"Full name: {message.from_user.full_name}\n"
                f"Username: {message.from_user.username}\n"
                f"Telegram id: {message.from_user.id}")
        await send_log_text(text=text)

        text = "👋 Welcome to the bot!"
        if referrer:
            text += f"\n🎉 You were invited by {referrer.first_name}."
            try:
                safe_name = escape(user.first_name or "Unknown")
                if user.username:
                    name = f"@{user.username}" 
                else:
                    name = f"<a href='tg://user?id={message.from_user.id}'>{safe_name}</a>"
                await message.bot.send_message(
                    referrer.telegram_id,
                    f"🎊 Your friend {name} just joined using your referral link!",
                    parse_mode="HTML"
                )
            except Exception as e:
                text = f"In user.py line 47\n{str(e)}"
                await send_log_text(text=text, type="error")
    else:
        text = "👋 Welcome back!"

    await message.answer(text)


@router.message(Command("friends"), F.chat.type == ChatType.PRIVATE)
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
    

@router.message(Command("admin"), F.chat.type == ChatType.PRIVATE)
async def contact_admin(message: Message):
    user = await create_or_update_user(message)
    await message.answer(text="Click on the button to contact with Admin", reply_markup=admin())


@router.message(Command("referral"), F.chat.type == ChatType.PRIVATE)
async def invite_friends(message: Message, command: CommandObject):
    user = await create_or_update_user(message)
    text = (f"Share this link: \n\n" 
            f"<b>{user.referral_link}</b>\n\n"
            f"Climb the leaderboard and get more referrals! 🥇🥈🥉")
    
    await message.answer(text=text, parse_mode="HTML")


@router.message(F.text.regexp(r'^\d+$'), F.chat.type == ChatType.PRIVATE)
async def send_movie(message: Message):
    user = await create_or_update_user(message)
    movie_id = int(message.text)

    try:
        await message.forward(chat_id=load_env.LOG_GROUP_ID)
    except Exception as e:
        print(str(e))
        
    partners = await sync_to_async(list)(PartnerChannels.objects.all())
    for partner in partners:
        subscribed = await is_subscribed(bot=message.bot, user_id=message.from_user.id,
                                            channel_id=partner.channel_id)
        if not subscribed:
            await message.answer(text="Subscribe to continue", reply_markup=channels_keyboard(partners))
            return
        
    # Get movie
    movie = await sync_to_async(Movies.objects.filter(id=movie_id).first)()
    if not movie:
        await message.answer("Movie with this ID was not found ❌")
        return

    # Extract message ID from telegram link (make sure link is correct)
    movie_link = movie.telegram_link

    try:
        message_id = int(movie_link.rstrip("/").split("/")[-1])
    except ValueError:
        print("Invalid movie link stored in database ❌")
        text = f"in user.py line 142\nInvalid movie link stored in database ❌"
        await send_log_text(text=text, type="error")
        return

    # Copy message from group
    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=load_env.GROUP_ID,
            message_id=message_id,
            protect_content=True
        )
    except Exception as e:
        text = f"in user.py line 153\n{str(e)}"
        await send_log_text(text=text, type="error")

    # If admin — send extra text
    if str(message.from_user.id) in load_env.ADMINS:
        text = await post_text(movie=movie)
        await message.answer(text=text, parse_mode="HTML")
    

