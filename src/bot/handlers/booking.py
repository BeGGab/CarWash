"""
Обработчики бронирования для Telegram бота CarWash
"""
import logging

import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.states import UserStates
from src.bot.keyboards.keyboards import (
    get_date_keyboard, get_time_slots_keyboard,
    get_wash_types_keyboard, get_booking_confirm_keyboard,
    get_main_keyboard, get_back_keyboard,
)
from src.services.users import find_user
from bot.utils.api_client import ApiClient
from src.core.config import Settings

logger = logging.getLogger(__name__)
router = Router(name="booking")

@router.callback_query(F.data.startswith("carwash_"))
async def show_carwash_detail(callback: CallbackQuery, state: FSMContext, api_client: ApiClient):
    """Показать детали автомойки"""
    carwash_id = callback.data.replace("carwash_", "")

    try:
        carwash = await api_client.get_carwash(carwash_id)

        await state.update_data(carwash_id=carwash_id, carwash_name=carwash["name"])

        text = f"""
🏢 <b>{carwash['name']}</b>

📍 Адрес: {carwash['address']}
📞 Телефон: {carwash['phone_number']}
⭐ Рейтинг: {carwash.get('rating', 'N/A')}
🕐 Время работы: {carwash['working_hours']['start']} - {carwash['working_hours']['end']}
"""
        # TODO: Добавить в API эндпоинт для получения кол-ва свободных слотов
        # text += f"\n✅ Свободных слотов сегодня: {carwash['available_slots']}"

        kb = get_date_keyboard(carwash_id)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

    except httpx.HTTPStatusError as e:
        logger.error(f"API error getting carwash detail: {e.response.text}")
        await callback.message.answer("❌ Не удалось загрузить информацию об автомойке.")
    except Exception as e:
        logger.error(f"Error getting carwash detail: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("select_date_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    """Выбор даты"""
    carwash_id = callback.data.replace("select_date_", "")
    
    kb = get_date_keyboard(carwash_id)
    await callback.message.edit_text("📅 <b>Выберите дату:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def show_time_slots(callback: CallbackQuery, state: FSMContext, api_client: ApiClient):
    """Показать слоты на выбранную дату"""
    parts = callback.data.split("_")
    carwash_id = parts[1]
    selected_date = parts[2]

    await state.update_data(selected_date=selected_date)

    try:
        slots = await api_client.get_time_slots(
            carwash_id=carwash_id, date=selected_date
        )

        if not slots:
            text = f"😔 <b>На {selected_date} свободных слотов нет.</b>"
        else:
            text = f"⏰ <b>Свободные слоты на {selected_date}:</b>"

        kb = get_time_slots_keyboard(carwash_id, selected_date, slots)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

    except httpx.HTTPStatusError as e:
        logger.error(f"API error getting time slots: {e.response.text}")
        await callback.message.answer("❌ Не удалось загрузить слоты.")
    except Exception as e:
        logger.error(f"Error getting time slots: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("slot_"))
async def select_slot(callback: CallbackQuery, state: FSMContext, api_client: ApiClient):
    """Выбор слота и типа мойки"""
    slot_id = callback.data.replace("slot_", "")

    await state.update_data(slot_id=slot_id)

    try:
        wash_types_data = await api_client.get_wash_types()
        wash_types = wash_types_data.get("items", [])

        kb = get_wash_types_keyboard(wash_types, slot_id)
        await callback.message.edit_text("🧽 <b>Выберите тип мойки:</b>", reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting wash types: {e}")
        await callback.message.answer("❌ Не удалось загрузить типы мойки. Попробуйте позже.")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("washtype_"))
async def select_wash_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа мойки и ввод данных авто"""
    parts = callback.data.split("_")
    slot_id = parts[1]
    wash_type_id = parts[2]
    
    await state.update_data(wash_type_id=wash_type_id)
    await state.set_state(UserStates.entering_car_plate)
    
    await callback.message.edit_text(
        "🚗 <b>Введите госномер автомобиля:</b>\n\n"
        "Например: А123БВ77",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(UserStates.entering_car_plate)
async def enter_car_plate(message: Message, state: FSMContext):
    """Ввод номера авто"""
    car_plate = message.text.upper().replace(" ", "")
    
    if len(car_plate) < 6:
        await message.answer("❌ Некорректный номер. Попробуйте ещё раз:")
        return
    
    await state.update_data(car_plate=car_plate)
    await state.set_state(UserStates.entering_car_model)
    
    await message.answer(
        "🚙 <b>Введите марку и модель автомобиля:</b>\n\n"
        "Например: Toyota Camry",
        parse_mode="HTML"
    )


@router.message(UserStates.entering_car_model)
async def enter_car_model(message: Message, state: FSMContext, api_client: ApiClient):
    """Ввод модели авто и подтверждение"""
    car_model = message.text

    await state.update_data(car_model=car_model)

    data = await state.get_data()
    price = 0
    try:
        price_data = await api_client.calculate_price(
            time_slot_id=data.get("slot_id"), wash_type_id=data.get("wash_type_id")
        )
        price = price_data.get("final_price", 0)
    except Exception as e:
        logger.error(f"Could not calculate price via API: {e}")
        # В случае ошибки можно установить цену по умолчанию или показать ошибку
        await message.answer("❌ Не удалось рассчитать стоимость. Попробуйте позже.")
        return

    prepayment = price * 0.5 if price > 0 else 0
    carwash_name = data.get("carwash_name", "Автомойка")
    selected_date = data.get("selected_date", "")
    car_plate = data.get("car_plate", "")

    await state.update_data(final_price=price)
    await state.set_state(UserStates.confirming_booking)

    text = f"""
✅ <b>Подтверждение бронирования</b>

🏢 {carwash_name}
� {selected_date}
🚙 {car_model} ({car_plate})

�💰 Стоимость: {price}₽
💳 Предоплата (50%): {prepayment:.0f}₽

Нажмите "Оплатить" для завершения бронирования.
"""

    kb = get_booking_confirm_keyboard()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext, settings: Settings, session: AsyncSession, api_client: ApiClient):
    """Переход к оплате"""
    data = await state.get_data()
    try:
        # 1. Получаем пользователя и его телефон
        user = await find_user(session, telegram_id=callback.from_user.id)
        if not user or not user.phone_number:
            await callback.message.answer("❌ Для бронирования необходимо подтвердить номер телефона в профиле.")
            await callback.answer()
            return

        # 2. Собираем данные для создания бронирования
        booking_payload = {
            "car_wash_id": data.get("carwash_id"),
            "time_slot_id": data.get("slot_id"),
            "wash_type_id": data.get("wash_type_id"),
            "guest_phone": user.phone_number,
            "guest_name": user.first_name or "Клиент",
            "car_plate": data.get("car_plate"),
            "car_model": data.get("car_model"),
            "return_url": f"https://t.me/{settings.bot_username}", # URL для возврата после оплаты
        }

        # 3. Отправляем запрос на создание бронирования в API
        booking_confirmation = await api_client.create_booking(booking_payload)

        payment_info = booking_confirmation.get("payment", {})
        payment_url = payment_info.get("confirmation_url")
        prepayment_amount = payment_info.get("prepayment_amount", 0)

        await callback.message.edit_text(
            f"💳 <b>Оплата бронирования</b>\n\n"
            f"Сумма к оплате: {prepayment_amount:.0f}₽\n\n"
            f"Для завершения бронирования перейдите по ссылке ниже.",
            parse_mode="HTML"
        )

        # Отправляем ссылку на оплату
        await callback.message.answer(f"🔗 Ваша ссылка для оплаты: {settings.api_base_url}{payment_url}")

        await state.clear()

    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get("detail", "Не удалось создать бронирование")
        logger.error(f"API error creating booking: {e.response.text}")
        await callback.message.answer(f"❌ Ошибка: {error_detail}")
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        await callback.message.answer("❌ Произошла непредвиденная ошибка. Попробуйте позже.")
    finally:
        await callback.answer()


@router.callback_query(F.data == "edit_booking")
async def edit_booking(callback: CallbackQuery, state: FSMContext):
    """Редактирование бронирования"""
    data = await state.get_data()
    carwash_id = data.get("carwash_id", "1")
    
    kb = get_date_keyboard(carwash_id)
    await callback.message.edit_text("📅 <b>Выберите другую дату:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "cancel_booking_flow")
async def cancel_booking_flow(callback: CallbackQuery, state: FSMContext, settings: Settings):
    """Отмена процесса бронирования"""
    await state.clear()
    
    kb = get_main_keyboard(callback.from_user.id, settings.admins_id, settings.webapp_url)
    await callback.message.edit_text("❌ Бронирование отменено", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "back_to_slots")
async def back_to_slots(callback: CallbackQuery, state: FSMContext, api_client: ApiClient):
    """Назад к выбору слотов"""
    data = await state.get_data()
    carwash_id = data.get("carwash_id")
    selected_date = data.get("selected_date", "")

    if not carwash_id or not selected_date:
        await callback.answer("Ошибка: не найдены данные о мойке или дате.", show_alert=True)
        return

    # Просто вызываем уже существующий обработчик для показа слотов
    await show_time_slots(callback, state, api_client)


@router.callback_query(F.data.startswith("pay_booking_"))
async def pay_existing_booking(callback: CallbackQuery, state: FSMContext):
    """Оплата существующего бронирования"""
    booking_id = callback.data.replace("pay_booking_", "")
    
    # TODO: Реализовать логику получения ссылки на оплату для существующего бронирования
    
    await callback.message.answer(
        f"💳 <b>Оплата бронирования #{booking_id[:6]}</b>\n\n"
        f"Функция оплаты для существующего бронирования в разработке.",
        parse_mode="HTML"
    )
    await callback.answer()
