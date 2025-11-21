from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatType
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from bot.states.admin import BroadcastStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.all import *
from bot.utils.send_movie import broadcast_ad
import load_env

from movies.models import Movies, PartnerChannels

router = Router()

@router.message(F.text == "📊 Stats", F.chat.type == ChatType.PRIVATE)
async def stats_handler(message:Message):
    if not str(message.from_user.id) in load_env.ADMINS:
        return
    users = await get_all_users()
    await message.answer(text=f"<b>The number of Bot Users: {len(users)}</b>", parse_mode="HTML")

@router.message(F.text == "📢 Send Message", F.chat.type == ChatType.PRIVATE)
async def start_handler(message: Message, state: FSMContext):
    if not str(message.from_user.id) in load_env.ADMINS:
        return
    await message.answer(text="Send the Message you want to send to all users")
    await state.set_state(BroadcastStates.waiting_for_content)


@router.message(BroadcastStates.waiting_for_content, F.chat.type == ChatType.PRIVATE)
async def receive_ad_content(message: Message, state: FSMContext):
    # Store the message ID and chat ID so we can copy it later
    await state.update_data(ad_message_id=message.message_id, ad_chat_id=message.chat.id)

    # Show preview with inline buttons
    preview_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Send", callback_data="broadcast_send")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="broadcast_cancel")]
    ])
    
    await message.answer("Choose the action:", reply_markup=preview_kb)
    await state.set_state(BroadcastStates.preview)


@router.callback_query(F.data == "broadcast_send", F.message.chat.type == ChatType.PRIVATE)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text("Broadcast started ✅", reply_markup=None)
    ad_message_id = data["ad_message_id"]
    ad_chat_id = data["ad_chat_id"]

    broadcast_ad.delay(ad_chat_id, ad_message_id)
    
    await state.clear()

@router.callback_query(F.data == "broadcast_cancel", F.message.chat.type == ChatType.PRIVATE)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text("Broadcast cancelled ❌", reply_markup=None)