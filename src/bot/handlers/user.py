"""
Обработчики команд пользователя для Telegram бота CarWash
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.states import UserStates
from src.bot.keyboards.keyboards import (
    get_main_keyboard, get_contact_keyboard, get_location_keyboard,
    get_profile_keyboard, get_carwashes_keyboard, get_my_bookings_keyboard,
    get_booking_detail_keyboard, get_confirm_cancel_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name="user")

ADMIN_IDS = []
WEBAPP_URL = None


def setup_config(admin_ids: list, webapp_url: str = None):
    global ADMIN_IDS, WEBAPP_URL
    ADMIN_IDS = admin_ids
    WEBAPP_URL = webapp_url


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    
    welcome_text = f"""
🚿 <b>Добро пожаловать в CarWash!</b>

Привет, {user.first_name}! 👋

Я помогу забронировать мойку без очередей:
✅ Найди ближайшую мойку
✅ Выбери удобное время  
✅ Оплати 50% онлайн
✅ Покажи QR-код на мойке

🚗 Давай начнём!
"""
    
    kb = get_main_keyboard(user.id, ADMIN_IDS, WEBAPP_URL)
    await message.answer(welcome_text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.edit_text("🚿 <b>Главное меню</b>\n\nВыберите действие:", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    is_verified = False
    
    profile_text = f"""
👤 <b>Ваш профиль</b>

📛 Имя: {user.first_name} {user.last_name or ''}
🆔 Username: @{user.username or 'не указан'}
📱 Телефон: {'✅ подтверждён' if is_verified else '❌ не подтверждён'}
"""
    
    kb = get_profile_keyboard(is_verified)
    await callback.message.edit_text(profile_text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "verify_phone")
async def request_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_for_phone)
    await callback.message.answer("📱 Отправьте ваш номер телефона:", reply_markup=get_contact_keyboard())
    await callback.answer()


@router.message(UserStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer("❌ Отправьте свой номер телефона")
        return
    
    await state.clear()
    await message.answer(f"✅ Номер {contact.phone_number} подтверждён!", reply_markup=ReplyKeyboardRemove())
    
    kb = get_main_keyboard(message.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await message.answer("Выберите действие:", reply_markup=kb)


@router.callback_query(F.data == "send_location")
async def request_location(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.selecting_location)
    await callback.message.answer("📍 Отправьте местоположение:", reply_markup=get_location_keyboard())
    await callback.answer()


@router.message(UserStates.selecting_location, F.location)
async def process_location(message: Message, state: FSMContext):
    location = message.location
    await state.update_data(latitude=location.latitude, longitude=location.longitude)
    
    await message.answer("📍 Ищу ближайшие мойки...", reply_markup=ReplyKeyboardRemove())
    
    # TODO: API запрос
    carwashes = [
        {"id": "1", "name": "АвтоСпа Premium", "distance": 1.2},
        {"id": "2", "name": "Чистый Кузов", "distance": 2.5},
    ]
    
    await state.clear()
    kb = get_carwashes_keyboard(carwashes)
    await message.answer(f"🏢 <b>Найдено {len(carwashes)} моек:</b>", reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "find_wash")
async def find_wash(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if not data.get('latitude'):
        await state.set_state(UserStates.selecting_location)
        await callback.message.answer("📍 Отправьте местоположение:", reply_markup=get_location_keyboard())
        await callback.answer()
        return
    
    carwashes = [{"id": "1", "name": "АвтоСпа Premium", "distance": 1.2}]
    kb = get_carwashes_keyboard(carwashes)
    await callback.message.edit_text(f"🏢 <b>Найдено {len(carwashes)} моек:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "my_bookings")
async def show_my_bookings(callback: CallbackQuery, state: FSMContext):
    # TODO: API запрос
    bookings = [{"id": "b1", "car_wash_name": "АвтоСпа", "slot_date": "25 янв", "start_time": "14:00", "status": "confirmed"}]
    
    text = "📅 <b>Ваши брони:</b>" if bookings else "📅 <b>Нет активных бронирований</b>"
    kb = get_my_bookings_keyboard(bookings, show_active=True)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("booking_"))
async def show_booking_detail(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]
    
    booking = {
        "id": booking_id, "car_wash_name": "АвтоСпа Premium", "car_wash_address": "ул. Ленина, 15",
        "slot_date": "25 января", "start_time": "14:00", "end_time": "14:30",
        "wash_type_name": "Стандарт", "car_plate": "А123БВ77", "car_model": "Toyota Camry",
        "final_price": 800, "payment_status": "paid", "status": "confirmed"
    }
    
    text = f"""
🚗 <b>Бронь #{booking_id[:6]}</b>

🏢 <b>{booking['car_wash_name']}</b>
📍 {booking['car_wash_address']}
📅 {booking['slot_date']} ⏰ {booking['start_time']}
🧽 {booking['wash_type_name']}
🚙 {booking['car_model']} ({booking['car_plate']})
💰 {booking['final_price']}₽ (предоплата 50%)
"""
    
    kb = get_booking_detail_keyboard(booking)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("cancel_booking_", "")
    kb = get_confirm_cancel_keyboard(booking_id)
    await callback.message.edit_text("❓ <b>Отменить бронирование?</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("confirm_cancel_", "")
    await callback.message.edit_text(f"✅ Бронь #{booking_id[:6]} отменена")
    
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.answer("Выберите действие:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("show_qr_"))
async def show_qr_code(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("show_qr_", "")
    await callback.message.answer(f"📱 <b>QR-код #{booking_id[:6]}</b>\n\nПокажите на мойке", parse_mode="HTML")
    await callback.answer("QR отправлен!")


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.edit_text("Отменено", reply_markup=kb)
    await callback.answer()
