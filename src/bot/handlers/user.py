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
from src.bot.utils.api_client import ApiClient
from src.bot.utils.datetime_utils import (
    format_date_for_display,
    format_time_for_display,
)
import httpx


from src.services.users import (
    find_user,
    create_user,
    get_user_carwash_admin_roles,
    verify_user as verify_user_service,
)
from src.schemas.users import SPhoneVerification, SUserCreate

from src.core.config import Settings


logger = logging.getLogger(__name__)
router = Router(name="user")


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, session: AsyncSession, settings: Settings
):
    """
    Обработчик команды /start. Проверяет, зарегистрирован ли пользователь.
    Если нет - запускает процесс регистрации.
    Если да - показывает главное меню.
    """
    try:
        # Пытаемся найти пользователя в БД
        user = await find_user(session, telegram_id=message.from_user.id)
        # Если пользователь найден, показываем главное меню
        admin_roles = await get_user_carwash_admin_roles(
            session, user_id=message.from_user.id
        )
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
        keyboard = kb.get_main_keyboard(
            user_id=message.from_user.id,
            system_admins=settings.admins_id,
            webapp_url=settings.webapp_url,
            carwash_admin_roles=admin_roles,
        )
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        # Если find_user выбросил исключение (пользователь не найден)
        await state.clear()
        # Предлагаем использовать имя из Telegram или ввести свое
        tg_first = message.from_user.first_name or " "
        name_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=tg_first)]],
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
async def back_to_menu(
    callback: CallbackQuery, state: FSMContext, settings: Settings, session: AsyncSession
):
    await state.clear()
    admin_roles = await get_user_carwash_admin_roles(
        session, user_id=callback.from_user.id
    )
    keyboard = kb.get_main_keyboard(
        user_id=callback.from_user.id,
        system_admins=settings.admins_id,
        webapp_url=settings.webapp_url,
        carwash_admin_roles=admin_roles,
    )
    await callback.message.edit_text(
        "🚿 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(StateFilter(UserStates.reg_name))
async def get_reg_name(message: Message, state: FSMContext):
    """Шаг 1 регистрации: получаем имя."""
    await state.update_data(first_name=message.text.strip())
    await message.answer(
        "Отлично! Теперь, пожалуйста, отправьте ваш номер телефона, "
        "нажав на кнопку ниже 📱",
        reply_markup=kb.get_contact_keyboard(),
    )
    await state.set_state(UserStates.reg_phone)


@router.message(
    StateFilter(UserStates.reg_phone), F.text.casefold() == "❌ отмена".casefold()
)
async def cancel_reg_phone(
    message: Message, state: FSMContext, settings: Settings, session: AsyncSession
):
    await state.clear()
    admin_roles = await get_user_carwash_admin_roles(
        session, user_id=message.from_user.id
    )
    keyboard = kb.get_main_keyboard(
        message.from_user.id, settings.admins_id, settings.webapp_url, admin_roles
    )
    await message.answer("❌ Отменено", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите действие:", reply_markup=keyboard)


@router.message(StateFilter(UserStates.reg_phone), F.text)
async def wrong_reg_phone(message: Message):
    """Обработка случая, когда вместо кнопки отправляют текст."""
    await message.answer(
        "❌ Неверный формат. Пожалуйста, нажмите на кнопку 'Отправить номер телефона' или 'Отмена'."
    )


@router.callback_query(F.data == "profile")
async def show_profile(
    callback: CallbackQuery, session: AsyncSession, settings: Settings
):
    """
    Отображает профиль пользователя, получая данные из БД.
    """
    try:
        db_user = await find_user(session, telegram_id=callback.from_user.id)
        is_verified = db_user.is_verified
        phone_number = db_user.phone_number
    except Exception:
        is_verified = False
        phone_number = None

    profile_text = f"""
👤 <b>Ваш профиль</b>

📛 Имя: {callback.from_user.first_name} {callback.from_user.last_name or ""}
🆔 Username: @{callback.from_user.username or "не указан"}
📱 Телефон: {phone_number or "❌ не подтверждён"}
"""

    keyboard = kb.get_profile_keyboard(is_verified, settings.webapp_url)
    await callback.message.edit_text(
        profile_text, reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "verify_phone")
async def request_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_for_phone)
    await callback.message.answer(
        "📱 Отправьте ваш номер телефона:", reply_markup=kb.get_contact_keyboard()
    )
    await callback.answer()


@router.message(
    StateFilter(UserStates.waiting_for_phone),
    F.text.casefold() == "❌ отмена".casefold(),
)
async def cancel_waiting_phone(
    message: Message, state: FSMContext, settings: Settings, session: AsyncSession
):
    await state.clear()
    admin_roles = await get_user_carwash_admin_roles(
        session, user_id=message.from_user.id
    )
    keyboard = kb.get_main_keyboard(
        message.from_user.id, settings.admins_id, settings.webapp_url, admin_roles
    )
    await message.answer("❌ Отменено", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите действие:", reply_markup=keyboard)


@router.message(UserStates.waiting_for_phone, F.contact)
@router.message(UserStates.reg_phone, F.contact)
async def process_phone(
    message: Message, state: FSMContext, session: AsyncSession, settings: Settings
):
    contact = message.contact
    if not contact or contact.user_id != message.from_user.id:
        await message.answer("❌ Отправьте свой номер телефона")
        return

    current_state = await state.get_state()
    if current_state == UserStates.reg_phone.state:
        # Завершение регистрации
        reg_data = await state.get_data()
        user_data = SUserCreate(
            telegram_id=message.from_user.id,
            first_name=reg_data.get("first_name"),
            username=message.from_user.username or f"user_{message.from_user.id}",
            phone_number=contact.phone_number,
            is_verified=True,
        )
        await create_user(session, user_data)
        await message.answer(
            "✅ Вы успешно зарегистрированы!", reply_markup=ReplyKeyboardRemove()
        )
    else:
        # Обновление номера для существующего пользователя
        verification_data = SPhoneVerification(
            telegram_id=message.from_user.id, phone_number=contact.phone_number
        )
        updated_user = await verify_user_service(session, verification_data)
        await message.answer(
            f"✅ Ваш номер {updated_user.phone_number} подтверждён!",
            reply_markup=ReplyKeyboardRemove(),
        )

    await state.clear()
    admin_roles = await get_user_carwash_admin_roles(
        session, user_id=message.from_user.id
    )
    keyboard = kb.get_main_keyboard(
        message.from_user.id, settings.admins_id, settings.webapp_url, admin_roles
    )
    await message.answer("✅ Готово!\n\nВыберите действие:", reply_markup=keyboard)


@router.callback_query(F.data == "send_location")
async def request_location(
    callback: CallbackQuery, state: FSMContext, settings: Settings
):
    await state.set_state(UserStates.selecting_location)
    await callback.message.answer(
        "📍 Отправьте местоположение:", reply_markup=kb.get_location_keyboard()
    )
    await callback.answer()


@router.message(UserStates.selecting_location, F.location)
async def process_location(message: Message, state: FSMContext, settings: Settings):
    location = message.location
    await state.update_data(latitude=location.latitude, longitude=location.longitude)

    await message.answer(
        "📍 Ищу ближайшие мойки...", reply_markup=ReplyKeyboardRemove()
    )
    try:
        carwashes = await ApiClient(settings.api_base_url).get_carwashes(
            latitude=location.latitude, longitude=location.longitude
        )

        await state.clear()

        if not carwashes:
            await message.answer(
                "😔 Поблизости не найдено автомоек. Попробуйте изменить местоположение."
            )
            return

        keyboard = kb.get_carwashes_keyboard(carwashes)
        await message.answer(
            f"🏢 <b>Найдено {len(carwashes)} моек поблизости:</b>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error getting carwashes by location: {e}")
        await message.answer("❌ Не удалось загрузить список моек. Попробуйте позже.")


@router.callback_query(F.data == "find_wash")
async def find_wash(callback: CallbackQuery, state: FSMContext, settings: Settings):
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
        f"🏢 <b>Найдено {len(carwashes)} моек:</b>",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "my_bookings")
async def show_my_bookings(
    callback: CallbackQuery, session: AsyncSession, api_client: ApiClient
):
    """Показывает активные бронирования пользователя, делая запрос к API."""
    try:
        user = await find_user(session, telegram_id=callback.from_user.id)
        if not user or not user.phone_number:
            await callback.message.edit_text(
                "📱 Для просмотра бронирований необходимо подтвердить номер телефона в профиле.",
                reply_markup=kb.get_back_keyboard("profile"),
                parse_mode="HTML",
            )
            await callback.answer()
            return

        # API запрос для получения бронирований
        bookings_data = await api_client.get_my_bookings(phone=user.phone_number)
        bookings = bookings_data.get("items", [])

        text = (
            "📅 <b>Ваши активные брони:</b>"
            if bookings
            else "📅 <b>У вас нет активных бронирований.</b>"
        )
        keyboard = kb.get_my_bookings_keyboard(
            bookings, show_active=True
        )  # bookings_data['items']
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        await callback.message.answer(
            "❌ Не удалось загрузить список бронирований. Попробуйте позже."
        )
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("booking_"))
async def show_booking_detail(
    callback: CallbackQuery, state: FSMContext, api_client: ApiClient
):
    """Показывает детали бронирования, делая запрос к API."""
    booking_id = callback.data.split("_", 1)[1]

    try:
        # API запрос для получения деталей бронирования
        booking = await api_client.get_booking_details(booking_id)

        formatted_date = format_date_for_display(booking["slot_date"])
        formatted_time = format_time_for_display(booking["start_time"])
        text = f"""
🚗 <b>Бронь #{booking_id[:6]}</b>

🏢 <b>{booking["car_wash_name"]}</b>
📍 {booking["car_wash_address"]}
📅 {formatted_date} ⏰ {formatted_time}
🧽 {booking["wash_type_name"]}
🚙 {booking["car_model"]} ({booking["car_plate"]})
💰 {booking["final_price"]}₽ (предоплата 50%)
"""
        keyboard = kb.get_booking_detail_keyboard(booking)
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    except httpx.HTTPStatusError as e:
        logger.error(f"API error getting booking detail: {e.response.text}")
        await callback.message.answer("❌ Не удалось загрузить детали бронирования.")
    except Exception as e:
        logger.error(f"Error getting booking detail: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(
    callback: CallbackQuery, state: FSMContext, settings: Settings
):
    booking_id = callback.data.replace("cancel_booking_", "")
    keyboard = kb.get_confirm_cancel_keyboard(booking_id)
    await callback.message.edit_text(
        "❓ <b>Отменить бронирование?</b>", reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(
    callback: CallbackQuery, state: FSMContext, settings: Settings, api_client: ApiClient, session: AsyncSession
):
    booking_id = callback.data.replace("confirm_cancel_", "")

    try:
        await api_client.cancel_booking(booking_id)

        await callback.message.edit_text(
            f"✅ Бронь #{booking_id[:6]} отменена. Средства будут возвращены в ближайшее время."
        )
        admin_roles = await get_user_carwash_admin_roles(
            session, user_id=callback.from_user.id
        )
        keyboard = kb.get_main_keyboard(
            callback.from_user.id, settings.admins_id, settings.webapp_url, admin_roles
        )
        await callback.message.answer("Выберите действие:", reply_markup=keyboard)

    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get(
            "detail", "Не удалось отменить бронирование"
        )
        logger.error(f"API error cancelling booking: {e.response.text}")
        await callback.message.answer(f"❌ Ошибка: {error_detail}")
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        await callback.message.answer("❌ Произошла непредвиденная ошибка.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("show_qr_"))
async def show_qr_code(callback: CallbackQuery, state: FSMContext):
    booking_id = callback.data.replace("show_qr_", "")
    # TODO: В реальном приложении QR-код нужно получать из данных бронирования
    # и генерировать картинку, а не просто текст.
    # Например, с помощью библиотеки qrcode.
    await callback.message.answer(
        f"📱 <b>QR-код для брони #{booking_id[:6]}</b>\n\n"
        f"<code>{booking_id}</code>\n\nПокажите этот код на мойке.",
        parse_mode="HTML",
    )
    await callback.answer("QR отправлен!")


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "edit_profile")
async def edit_profile_fallback(callback: CallbackQuery):
    """
    Запасной обработчик на случай, если webapp_url не задан
    и кнопка 'Редактировать' использует callback_data.
    """
    await callback.answer(
        "Редактирование профиля доступно в Mini App.", show_alert=True
    )


@router.callback_query(F.data == "cancel")
async def cancel_handler(
    callback: CallbackQuery, state: FSMContext, settings: Settings, session: AsyncSession
):
    await state.clear()
    admin_roles = await get_user_carwash_admin_roles(
        session, user_id=callback.from_user.id
    )
    keyboard = kb.get_main_keyboard(
        callback.from_user.id, settings.admins_id, settings.webapp_url, admin_roles
    )
    await callback.message.edit_text("Отменено", reply_markup=keyboard)
    await callback.answer()
