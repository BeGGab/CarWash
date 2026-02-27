"""
Обработчики для системного администратора.
"""

import logging
import httpx

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.states import AdminWashStates
from src.bot.utils.api_client import ApiClient
from src.bot.keyboards.keyboards import get_main_keyboard, get_back_keyboard
from src.core.config import Settings

settings = Settings()

logger = logging.getLogger(__name__)
router = Router(name="system_admin")


# ==================== Системный админ ====================


@router.callback_query(F.data == "add_wash")
async def add_wash_start(
    callback: CallbackQuery, state: FSMContext, settings: Settings
):
    """Начало добавления мойки"""
    if callback.from_user.id not in settings.admins_id:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    await state.set_state(AdminWashStates.adding_wash_name)
    await callback.message.edit_text(
        "📝 <b>Добавление автомойки</b>\n\nВведите название:", parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminWashStates.adding_wash_name)
async def add_wash_name(message: Message, state: FSMContext):
    """Ввод названия мойки"""
    await state.update_data(wash_name=message.text)
    await state.set_state(AdminWashStates.adding_wash_address)
    await message.answer("📍 Введите адрес мойки:")


@router.message(AdminWashStates.adding_wash_address)
async def add_wash_address(message: Message, state: FSMContext):
    """Ввод адреса мойки"""
    await state.update_data(wash_address=message.text)
    await state.set_state(AdminWashStates.adding_wash_phone)
    await message.answer("📞 Введите телефон мойки (формат +7XXXXXXXXXX):")


@router.message(AdminWashStates.adding_wash_phone)
async def add_wash_phone(message: Message, state: FSMContext):
    """Ввод телефона мойки"""
    phone = message.text.replace(" ", "").replace("-", "")

    if not phone.startswith("+7") or len(phone) != 12:
        await message.answer("❌ Неверный формат. Используйте +7XXXXXXXXXX:")
        return

    await state.update_data(wash_phone=phone)
    await state.set_state(AdminWashStates.adding_wash_hours)
    await message.answer("🕐 Введите часы работы (формат: 08:00-22:00):")


@router.message(AdminWashStates.adding_wash_hours)
async def add_wash_hours(message: Message, state: FSMContext, api_client: ApiClient):
    """Ввод часов работы"""
    try:
        start, end = message.text.split("-")
        start = start.strip()
        end = end.strip()

        # Валидация времени
        start_h, start_m = map(int, start.split(":"))
        end_h, end_m = map(int, end.split(":"))

        if not (0 <= start_h <= 23 and 0 <= start_m <= 59):
            raise ValueError()
        if not (0 <= end_h <= 23 and 0 <= end_m <= 59):
            raise ValueError()

    except:
        await message.answer("❌ Неверный формат. Используйте HH:MM-HH:MM:")
        return

    await state.update_data(working_hours={"start": start, "end": end})

    state_data = await state.get_data()

    # Формируем данные для отправки в API
    carwash_data = {
        "name": state_data.get("wash_name"),
        "address": state_data.get("wash_address"),
        "phone_number": state_data.get("wash_phone"),
        # Отправляем часы работы как единый объект, как ожидает API
        "working_hours": state_data.get("working_hours"),
    }

    try:
        # Сохранение в БД через API
        await api_client.create_carwash(carwash_data)

        text = f"""
✅ <b>Автомойка добавлена!</b>

🏢 {carwash_data["name"]}
📍 {carwash_data["address"]}
📞 {carwash_data["phone_number"]}
🕐 {start} - {end}

Слоты будут автоматически созданы на 30 дней вперёд.
"""
        await state.clear()
        await message.answer(text, parse_mode="HTML")
    except httpx.HTTPStatusError as e:
        logger.error(f"API error on carwash creation: {e.response.text}")
        await message.answer(
            f"❌ Ошибка при создании мойки: {e.response.json().get('detail', 'Ошибка сервера')}"
        )
    except Exception as e:
        logger.error(f"Unexpected error on carwash creation: {e}")
        await message.answer("❌ Произошла непредвиденная ошибка. Попробуйте позже.")

    kb = get_main_keyboard(message.from_user.id, settings.admins_id)
    # В реальном приложении здесь нужно будет передать и роли админа мойки
    # Для простоты пока оставляем так
    await message.answer("Главное меню:", reply_markup=kb) 


@router.callback_query(F.data == "del_wash")
async def del_wash_start(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    api_client: ApiClient,
):
    """Удаление мойки"""
    if callback.from_user.id not in settings.admins_id:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    try:
        # Получаем список моек из API
        washes = await api_client.get_carwashes()

        if not washes:
            await callback.message.edit_text(
                "ℹ️ В системе пока нет автомоек для удаления.",
                reply_markup=get_back_keyboard("back_to_menu"),
            )
            await callback.answer()
            return

        buttons = []
        for w in washes:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🗑 {w['name']}", callback_data=f"del_{w['id']}"
                    )
                ]
            )
        buttons.append(
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        )

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(
            "🗑 <b>Выберите мойку для удаления:</b>", reply_markup=kb, parse_mode="HTML"
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"API error on getting carwashes: {e.response.text}")
        await callback.message.answer(
            f"❌ Ошибка при получении списка моек: {e.response.json().get('detail', 'Ошибка сервера')}"
        )
    except Exception as e:
        logger.error(f"Unexpected error on getting carwashes: {e}")
        await callback.message.answer(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("del_"))
async def del_wash_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    api_client: ApiClient,
):
    """Подтверждение удаления"""
    wash_id = callback.data.replace("del_", "")

    try:
        await api_client.delete_carwash(wash_id)

        await callback.message.edit_text(f"✅ Мойка успешно удалена.")
        # Аналогично, здесь может потребоваться обновление ролей
        kb = get_main_keyboard(callback.from_user.id, settings.admins_id)
        await callback.message.answer("Главное меню:", reply_markup=kb)

    except httpx.HTTPStatusError as e:
        logger.error(f"API error on carwash deletion: {e.response.text}")
        await callback.message.answer(
            f"❌ Ошибка при удалении мойки: {e.response.json().get('detail', 'Ошибка сервера')}"
        )
    except Exception as e:
        logger.error(f"Unexpected error on carwash deletion: {e}")
        await callback.message.answer(
            "❌ Произошла непредвиденная ошибка. Попробуйте позже."
        )
    finally:
        await callback.answer()


@router.callback_query(F.data == "stats")
async def show_stats(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: ApiClient,
):
    """Показать статистику"""
    if callback.from_user.id not in settings.admins_id:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    stats = await api_client.get_system_stats()

    text = f"""
📊 <b>Статистика системы</b>

🏢 Всего моек: {stats.get("carwashes_count", 0)}
📅 Всего бронирований: {stats.get("total_bookings", 0)}

⭐ Подтверждённых бронирований: {stats.get("confirmed_bookings", 0)}
"""

    kb = get_back_keyboard("back_to_menu")
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# ==================== Управление админами моек ====================


@router.callback_query(F.data == "manage_wash_admins")
async def manage_wash_admins_start(
    callback: CallbackQuery,
    settings: Settings,
    api_client: ApiClient,
):
    """Выбор мойки для управления администраторами"""
    if callback.from_user.id not in settings.admins_id:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    washes = await api_client.get_carwashes()
    if not washes:
        await callback.message.edit_text(
            "ℹ️ Сначала добавьте хотя бы одну автомойку.",
            reply_markup=get_back_keyboard("back_to_menu"),
        )
        await callback.answer()
        return

    buttons = [
        [
            InlineKeyboardButton(
                text=f"🧑‍💼 {w['name']}", callback_data=f"set_admin_{w['id']}"
            )
        ]
        for w in washes
    ]
    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    )
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "Выберите мойку для назначения администратора:", reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_admin_"))
async def set_admin_for_wash(callback: CallbackQuery, state: FSMContext):
    """Начало процесса назначения админа"""
    carwash_id = callback.data.replace("set_admin_", "")
    await state.set_state(AdminWashStates.adding_wash_admin_phone)
    await state.update_data(carwash_id=carwash_id)
    await callback.message.edit_text(
        "📞 Введите номер телефона пользователя, которого хотите сделать "
        "администратором этой мойки (формат +7XXXXXXXXXX).\n\n"
        "Пользователь должен быть зарегистрирован в боте."
    )
    await callback.answer()


@router.message(AdminWashStates.adding_wash_admin_phone)
async def add_wash_admin_phone(
    message: Message, state: FSMContext, api_client: ApiClient, settings: Settings
):
    """Добавление админа по номеру телефона"""
    phone = message.text.strip()
    if not phone.startswith("+7") or len(phone) != 12:
        await message.answer("❌ Неверный формат. Используйте +7XXXXXXXXXX:")
        return

    data = await state.get_data()
    carwash_id = data.get("carwash_id")

    try:
        await api_client.add_carwash_admin(carwash_id, phone)
        await message.answer(f"✅ Пользователь с номером {phone} назначен администратором.")
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Неизвестная ошибка API")
        await message.answer(f"❌ Ошибка: {detail}")
    except Exception as e:
        logger.error(f"Error adding carwash admin: {e}")
        await message.answer("❌ Произошла непредвиденная ошибка.")
    finally:
        await state.clear()
        kb = get_main_keyboard(message.from_user.id, settings.admins_id)
        await message.answer("Главное меню:", reply_markup=kb)
