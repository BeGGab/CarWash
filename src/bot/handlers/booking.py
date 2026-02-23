"""
Обработчики бронирования для Telegram бота CarWash
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states import UserStates
from src.bot.keyboards.keyboards import (
    get_date_keyboard, get_time_slots_keyboard,
    get_wash_types_keyboard, get_booking_confirm_keyboard,
    get_main_keyboard, get_back_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name="booking")

ADMIN_IDS = []
WEBAPP_URL = None


def setup_config(admin_ids: list, webapp_url: str = None):
    global ADMIN_IDS, WEBAPP_URL
    ADMIN_IDS = admin_ids
    WEBAPP_URL = webapp_url


@router.callback_query(F.data.startswith("carwash_"))
async def show_carwash_detail(callback: CallbackQuery, state: FSMContext):
    """Показать детали автомойки"""
    carwash_id = callback.data.replace("carwash_", "")
    
    # TODO: API запрос
    carwash = {
        "id": carwash_id,
        "name": "АвтоСпа Premium",
        "address": "ул. Ленина, 15",
        "phone": "+7 (999) 123-45-67",
        "rating": 4.8,
        "working_hours": {"start": "08:00", "end": "22:00"},
        "available_slots": 5
    }
    
    await state.update_data(carwash_id=carwash_id, carwash_name=carwash["name"])
    
    text = f"""
🏢 <b>{carwash['name']}</b>

📍 Адрес: {carwash['address']}
📞 Телефон: {carwash['phone']}
⭐ Рейтинг: {carwash['rating']}
🕐 Время работы: {carwash['working_hours']['start']} - {carwash['working_hours']['end']}

✅ Свободных слотов сегодня: {carwash['available_slots']}
"""
    
    kb = get_date_keyboard(carwash_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("select_date_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    """Выбор даты"""
    carwash_id = callback.data.replace("select_date_", "")
    
    kb = get_date_keyboard(carwash_id)
    await callback.message.edit_text("📅 <b>Выберите дату:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def show_time_slots(callback: CallbackQuery, state: FSMContext):
    """Показать слоты на выбранную дату"""
    parts = callback.data.split("_")
    carwash_id = parts[1]
    selected_date = parts[2]
    
    await state.update_data(selected_date=selected_date)
    
    # TODO: API запрос
    slots = [
        {"id": "slot1", "start_time": "10:00", "end_time": "10:30"},
        {"id": "slot2", "start_time": "10:30", "end_time": "11:00"},
        {"id": "slot3", "start_time": "11:00", "end_time": "11:30"},
        {"id": "slot4", "start_time": "14:00", "end_time": "14:30"},
        {"id": "slot5", "start_time": "15:00", "end_time": "15:30"},
    ]
    
    kb = get_time_slots_keyboard(carwash_id, selected_date, slots)
    await callback.message.edit_text(
        f"⏰ <b>Свободные слоты на {selected_date}:</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("slot_"))
async def select_slot(callback: CallbackQuery, state: FSMContext):
    """Выбор слота и типа мойки"""
    slot_id = callback.data.replace("slot_", "")
    
    await state.update_data(slot_id=slot_id)
    
    # TODO: API запрос
    wash_types = [
        {"id": "wt1", "name": "Экспресс", "duration_minutes": 15, "base_price": 400},
        {"id": "wt2", "name": "Стандарт", "duration_minutes": 30, "base_price": 700},
        {"id": "wt3", "name": "Премиум", "duration_minutes": 45, "base_price": 1200},
        {"id": "wt4", "name": "Люкс + химчистка", "duration_minutes": 90, "base_price": 2500},
    ]
    
    kb = get_wash_types_keyboard(wash_types, slot_id)
    await callback.message.edit_text("🧽 <b>Выберите тип мойки:</b>", reply_markup=kb, parse_mode="HTML")
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
async def enter_car_model(message: Message, state: FSMContext):
    """Ввод модели авто и подтверждение"""
    car_model = message.text
    
    await state.update_data(car_model=car_model)
    
    data = await state.get_data()
    
    # TODO: Получить цену из API
    price = 700
    prepayment = price * 0.5
    
    booking_data = {
        "temp_id": "new",
        "carwash_name": data.get("carwash_name", "Автомойка"),
        "selected_date": data.get("selected_date", ""),
        "car_plate": data.get("car_plate", ""),
        "car_model": car_model,
        "final_price": price
    }
    
    await state.update_data(booking_data=booking_data, final_price=price)
    await state.set_state(UserStates.confirming_booking)
    
    text = f"""
✅ <b>Подтверждение бронирования</b>

🏢 {booking_data['carwash_name']}
📅 {booking_data['selected_date']}
🚙 {booking_data['car_model']} ({booking_data['car_plate']})

💰 Стоимость: {price}₽
💳 Предоплата (50%): {prepayment:.0f}₽

Нажмите "Оплатить" для завершения бронирования.
"""
    
    kb = get_booking_confirm_keyboard({"temp_id": "new", "final_price": price})
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    """Переход к оплате"""
    data = await state.get_data()
    price = data.get("final_price", 700)
    prepayment = price * 0.5
    
    # TODO: Создание платежа через API
    # payment_url = await create_payment(booking_id, prepayment)
    
    await callback.message.edit_text(
        f"💳 <b>Оплата бронирования</b>\n\n"
        f"Сумма к оплате: {prepayment:.0f}₽\n\n"
        f"🔗 Ссылка для оплаты будет отправлена отдельным сообщением.\n\n"
        f"После оплаты вы получите QR-код для входа на мойку.",
        parse_mode="HTML"
    )
    
    # Симуляция успешной оплаты для демо
    await callback.message.answer(
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        "Ваше бронирование подтверждено.\n"
        "QR-код доступен в разделе 'Мои брони'.",
        parse_mode="HTML"
    )
    
    await state.clear()
    
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.answer("Выберите действие:", reply_markup=kb)
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
async def cancel_booking_flow(callback: CallbackQuery, state: FSMContext):
    """Отмена процесса бронирования"""
    await state.clear()
    
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS, WEBAPP_URL)
    await callback.message.edit_text("❌ Бронирование отменено", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "back_to_slots")
async def back_to_slots(callback: CallbackQuery, state: FSMContext):
    """Назад к выбору слотов"""
    data = await state.get_data()
    carwash_id = data.get("carwash_id", "1")
    selected_date = data.get("selected_date", "")
    
    # TODO: API запрос
    slots = [
        {"id": "slot1", "start_time": "10:00"},
        {"id": "slot2", "start_time": "10:30"},
        {"id": "slot3", "start_time": "11:00"},
    ]
    
    kb = get_time_slots_keyboard(carwash_id, selected_date, slots)
    await callback.message.edit_text(f"⏰ <b>Слоты на {selected_date}:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("pay_booking_"))
async def pay_existing_booking(callback: CallbackQuery, state: FSMContext):
    """Оплата существующего бронирования"""
    booking_id = callback.data.replace("pay_booking_", "")
    
    # TODO: Создание платежа через API
    
    await callback.message.answer(
        f"💳 <b>Оплата бронирования #{booking_id[:6]}</b>\n\n"
        f"Ссылка для оплаты отправлена.",
        parse_mode="HTML"
    )
    await callback.answer()
