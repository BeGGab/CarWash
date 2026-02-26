"""
Обработчики для администратора автомойки
"""

import uuid
import logging
import httpx
from datetime import date

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states import AdminWashStates
from src.bot.utils.api_client import ApiClient
from src.bot.keyboards.keyboards import get_main_keyboard, get_back_keyboard
from src.core.config import Settings

logger = logging.getLogger(__name__)
router = Router(name="carwash_admin")


@router.callback_query(F.data.startswith("wa_today_"))
async def wash_admin_today(
    callback: CallbackQuery,
    api_client: ApiClient,
):
    """Брони на сегодня для админа мойки"""
    carwash_id = callback.data.replace("wa_today_", "")
    today = date.today().isoformat()

    try:
        bookings_page = await api_client.get_carwash_bookings(
            carwash_id=carwash_id,
            date_from=today,
            date_to=today,
        )

        status_icons = {
            "pending_payment": "⏳",
            "confirmed": "✅",
            "in_progress": "🔄",
            "completed": "✔️",
        }

        if not bookings_page.get("items"):
            lines = ["📋 <b>На сегодня бронирований нет.</b>"]
        else:
            lines = ["📋 <b>Брони на сегодня:</b>\n"]
            for b in bookings_page["items"]:
                icon = status_icons.get(b["status"], "❓")
                # Время нужно будет отформатировать
                start_time = b.get("start_time", "??:??")[:5]
                lines.append(
                    f"{icon} {start_time} - {b.get('car_plate', 'Без номера')}"
                )

        kb = get_back_keyboard("back_to_menu")
        await callback.message.edit_text(
            "\n".join(lines), reply_markup=kb, parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error getting today's bookings for carwash {carwash_id}: {e}")
        await callback.message.answer("❌ Не удалось загрузить бронирования.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("wa_scan_"))
async def wash_admin_scan(callback: CallbackQuery, state: FSMContext):
    """Сканирование QR для админа мойки"""
    carwash_id = callback.data.replace("wa_scan_", "")

    await state.set_state(AdminWashStates.scanning_qr)
    await state.update_data(carwash_id=carwash_id)

    await callback.message.edit_text(
        "📷 <b>Сканирование QR-кода</b>\n\n"
        "Отправьте фото QR-кода клиента или введите код вручную:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminWashStates.scanning_qr)
async def process_qr_scan(message: Message, state: FSMContext, api_client: ApiClient):
    """Обработка QR-кода"""
    qr_code = message.text

    try:
        # Предполагаем, что QR-код содержит booking_id
        booking_id = qr_code
        result = await api_client.verify_qr_code(booking_id, qr_code)

        booking = result.get("booking") if result.get("valid") else None

        if booking:
            text = f"""
✅ <b>QR-код подтверждён!</b>

👤 {booking["guest_name"]}
🚗 {booking["car_model"]} ({booking["car_plate"]})
🧽 Статус: {booking["status"]}
"""
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="▶️ Начать мойку",
                            callback_data=f"start_wash_{booking['id']}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 Назад", callback_data="back_to_menu"
                        )
                    ],
                ]
            )
            await state.clear()
            await message.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer("❌ QR-код не найден или недействителен")
    except Exception as e:
        logger.error(f"Error verifying QR code: {e}")
        await message.answer("❌ Ошибка при проверке QR-кода.")


@router.callback_query(F.data.startswith("start_wash_"))
async def start_wash(callback: CallbackQuery, api_client: ApiClient):
    """Начать мойку"""
    booking_id = callback.data.replace("start_wash_", "")
    try:
        await api_client.start_wash(booking_id)
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Завершить мойку",
                        callback_data=f"complete_wash_{booking_id}",
                    )
                ],
            ]
        )
        await callback.message.edit_text(
            f"🔄 <b>Мойка #{booking_id[:6]} начата</b>\n\nНажмите 'Завершить' по окончании работы.",
            reply_markup=kb,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error starting wash {booking_id}: {e}")
        await callback.message.answer("❌ Не удалось начать мойку.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("complete_wash_"))
async def complete_wash(
    callback: CallbackQuery, api_client: ApiClient, settings: Settings
):
    """Завершить мойку"""
    booking_id = callback.data.replace("complete_wash_", "")
    await api_client.complete_wash(booking_id)
    await callback.message.edit_text(
        f"✅ <b>Мойка #{booking_id[:6]} завершена!</b>", parse_mode="HTML"
    )
    kb = get_main_keyboard(
        callback.from_user.id, settings.admins_id, settings.webapp_url
    )
    await callback.message.answer("Главное меню:", reply_markup=kb)
    await callback.answer()
