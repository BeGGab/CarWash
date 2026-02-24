"""
Обработчики команд пользователя для Telegram бота CarWash
"""

import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.states import UserStates
import src.bot.keyboards.keyboards as kb


from src.services.users import (
    find_user,
    create_user,
    verify_user as verify_user_service,
)
from src.schemas.users import SPhoneVerification, SUserCreate

from src.core.config import Settings

setting = Settings()


logger = logging.getLogger(__name__)
router = Router(name="user")

ADMIN_IDS = [setting.admins_id]
WEBAPP_URL = setting.webapp_url


def setup_config(admin_ids: list, webapp_url: str = None):
    global ADMIN_IDS, WEBAPP_URL
    ADMIN_IDS = admin_ids
    WEBAPP_URL = webapp_url


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """
    Обработчик команды /start. Проверяет, зарегистрирован ли пользователь.
    Если нет - запускает процесс регистрации.
    Если да - показывает главное меню.
    """
    try:
        # Пытаемся найти пользователя в БД
        await find_user(session, telegram_id=message.from_user.id)
        # Если пользователь найден, показываем главное меню
        await state.clear()
        welcome_text = f"""
🚿 <b>Добро пожаловать в CarWash!</b>

Привет, {message.from_user.first_name}! 👋

Я помогу забронировать мойку без очередей:
✅ Найди ближайшую мойку
✅ Выбери удобное время  
✅ Оплати 50% онлайн
✅ Покажи QR-код на мойке

🚗 Давай начнём!
"""
        keyboard = kb.get_main_keyboard(message.from_user.id, ADMIN_IDS, WEBAPP_URL)
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        # Если find_user выбросил исключение (пользователь не найден)
        await state.clear()
        # Предлагаем использовать имя из Telegram или ввести свое
        name_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=message.from_user.first_name)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            "👋 Добро пожаловать! Похоже, вы у нас впервые.\n\n"
            "Давайте зарегистрируемся. Введите ваше имя ✍️",
            reply_markup=name_kb,
        )
        await state.set_state(UserStates.reg_name)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = kb.get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.edit_text(
        "🚿 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(StateFilter(UserStates.reg_name))
async def get_reg_name(message: Message, state: FSMContext):
    """Шаг 1 регистрации: получаем имя."""
    await state.update_data(first_name=message.text)
    await message.answer(
        "Отлично! Теперь, пожалуйста, отправьте ваш номер телефона, "
        "нажав на кнопку ниже 📱",
        reply_markup=kb.get_contact_keyboard(),
    )
    await state.set_state(UserStates.reg_phone)


@router.message(StateFilter(UserStates.reg_phone), F.text)
async def wrong_reg_phone(message: Message):
    """Обработка случая, когда вместо кнопки отправляют текст."""
    await message.answer(
        "❌ Неверный формат. Пожалуйста, нажмите на кнопку 'Отправить мой номер'."
    )


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, session: AsyncSession):
    """
    Отображает профиль пользователя, получая данные из БД.
    """
    try:
        # Ищем пользователя в БД через сервисный слой
        db_user = await find_user(session, telegram_id=callback.from_user.id)
        is_verified = db_user.is_verified
        phone_number = db_user.phone_number
    except Exception:
        # Если пользователь не найден в нашей БД (например, новый)
        is_verified = False
        phone_number = None

    profile_text = f"""
👤 <b>Ваш профиль</b>

📛 Имя: {callback.from_user.first_name} {callback.from_user.last_name or ""}
🆔 Username: @{callback.from_user.username or "не указан"}
📱 Телефон: {phone_number or "❌ не подтверждён"}
"""

    keyboard = kb.get_profile_keyboard(is_verified)
    await callback.message.edit_text(profile_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "verify_phone")
async def request_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_for_phone)
    await callback.message.answer(
        "📱 Отправьте ваш номер телефона:", reply_markup=kb.get_contact_keyboard()
    )
    await callback.answer()


@router.message(UserStates.waiting_for_phone, F.contact)
@router.message(
    UserStates.reg_phone, F.contact
)
async def process_phone(message: Message, state: FSMContext, session: AsyncSession):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer("❌ Отправьте свой номер телефона")
        return

    current_state = await state.get_state()
    if current_state == UserStates.reg_phone.state:
        # Завершение регистрации
        reg_data = await state.get_data()
        user_data = SUserCreate(
            telegram_id=message.from_user.id,
            first_name=reg_data.get("first_name"),
            username=message.from_user.username,
            phone_number=contact.phone_number,
            is_verified=True,
        )
        await create_user(session, user_data)
        await message.answer(
            "✅ Вы успешно зарегистрированы!", reply_markup=ReplyKeyboardRemove()
        )
    else:
        # Простое обновление номера для уже существующего пользователя
        verification_data = SPhoneVerification(
            telegram_id=message.from_user.id, phone_number=contact.phone_number
        )
        updated_user = await verify_user_service(session, verification_data)
        await message.answer(
            f"✅ Ваш номер {updated_user.phone_number} подтверждён!",
            reply_markup=ReplyKeyboardRemove(),
        )

    await state.clear()
    keyboard = kb.get_main_keyboard(message.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await message.answer("✅ Регистрация завершена!\n\nВыберите действие:", reply_markup=keyboard)


@router.callback_query(F.data == "send_location")
async def request_location(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.selecting_location)
    await callback.message.answer(
        "📍 Отправьте местоположение:", reply_markup=kb.get_location_keyboard()
    )
    await callback.answer()


@router.message(UserStates.selecting_location, F.location)
async def process_location(message: Message, state: FSMContext):
    location = message.location
    await state.update_data(latitude=location.latitude, longitude=location.longitude)

    await message.answer(
        "📍 Ищу ближайшие мойки...", reply_markup=ReplyKeyboardRemove()
    )

    # TODO: API запрос
    carwashes = [
        {"id": "1", "name": "АвтоСпа Premium", "distance": 1.2},
        {"id": "2", "name": "Чистый Кузов", "distance": 2.5},
    ]

    await state.clear()
    keyboard = kb.get_carwashes_keyboard(carwashes)
    await message.answer(
        f"🏢 <b>Найдено {len(carwashes)} моек:</b>", reply_markup=keyboard, parse_mode="HTML"
    )


@router.callback_query(F.data == "find_wash")
async def find_wash(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not data.get("latitude"):
        await state.set_state(UserStates.selecting_location)
        await callback.message.answer(
            "📍 Отправьте местоположение:", reply_markup=kb.get_location_keyboard()
        )
        await callback.answer()
        return

    carwashes = [{"id": "1", "name": "АвтоСпа Premium", "distance": 1.2}]
    keyboard = kb.get_carwashes_keyboard(carwashes)
    await callback.message.edit_text(
        f"🏢 <b>Найдено {len(carwashes)} моек:</b>", reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_bookings")
async def show_my_bookings(callback: CallbackQuery, state: FSMContext):
    # TODO: API запрос
    bookings = [
        {
            "id": "b1",
            "car_wash_name": "АвтоСпа",
            "slot_date": "25 янв",
            "start_time": "14:00",
            "status": "confirmed",
        }
    ]

    text = (
        "📅 <b>Ваши брони:</b>" if bookings else "📅 <b>Нет активных бронирований</b>"
    )
    keyboard = kb.get_my_bookings_keyboard(bookings, show_active=True)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("booking_"))
async def show_booking_detail(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]

    booking = {
        "id": booking_id,
        "car_wash_name": "АвтоСпа Premium",
        "car_wash_address": "ул. Ленина, 15",
        "slot_date": "25 января",
        "start_time": "14:00",
        "end_time": "14:30",
        "wash_type_name": "Стандарт",
        "car_plate": "А123БВ77",
        "car_model": "Toyota Camry",
        "final_price": 800,
        "payment_status": "paid",
        "status": "confirmed",
    }

    text = f"""
🚗 <b>Бронь #{booking_id[:6]}</b>

🏢 <b>{booking["car_wash_name"]}</b>
📍 {booking["car_wash_address"]}
📅 {booking["slot_date"]} ⏰ {booking["start_time"]}
🧽 {booking["wash_type_name"]}
🚙 {booking["car_model"]} ({booking["car_plate"]})
💰 {booking["final_price"]}₽ (предоплата 50%)
"""

    keyboard = kb.get_booking_detail_keyboard(booking)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("cancel_booking_", "")
    keyboard = kb.get_confirm_cancel_keyboard(booking_id)
    await callback.message.edit_text(
        "❓ <b>Отменить бронирование?</b>", reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("confirm_cancel_", "")
    await callback.message.edit_text(f"✅ Бронь #{booking_id[:6]} отменена")

    keyboard = kb.get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.answer("Выберите действие:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("show_qr_"))
async def show_qr_code(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("show_qr_", "")
    await callback.message.answer(
        f"📱 <b>QR-код #{booking_id[:6]}</b>\n\nПокажите на мойке", parse_mode="HTML"
    )
    await callback.answer("QR отправлен!")


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = kb.get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.edit_text("Отменено", reply_markup=keyboard)
    await callback.answer()
