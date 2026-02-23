"""
Обработчики для администратора автомойки
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states import AdminWashStates, SystemAdminStates
from src.bot.keyboards.keyboards import get_main_keyboard, get_back_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_wash")

ADMIN_IDS = []


def setup_config(admin_ids: list):
    global ADMIN_IDS
    ADMIN_IDS = admin_ids


# ==================== Системный админ ====================

@router.callback_query(F.data == "add_wash")
async def add_wash_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления мойки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminWashStates.adding_wash_name)
    await callback.message.edit_text("📝 <b>Добавление автомойки</b>\n\nВведите название:", parse_mode="HTML")
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
async def add_wash_hours(message: Message, state: FSMContext):
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
    
    data = await state.get_data()
    
    # TODO: Сохранение в БД через API
    
    text = f"""
✅ <b>Автомойка добавлена!</b>

🏢 {data['wash_name']}
📍 {data['wash_address']}
📞 {data['wash_phone']}
🕐 {start} - {end}

Слоты будут автоматически созданы на 30 дней вперёд.
"""
    
    await state.clear()
    await message.answer(text, parse_mode="HTML")
    
    kb = get_main_keyboard(message.from_user.id, ADMIN_IDS)
    await message.answer("Главное меню:", reply_markup=kb)


@router.callback_query(F.data == "del_wash")
async def del_wash_start(callback: CallbackQuery, state: FSMContext):
    """Удаление мойки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # TODO: Получить список моек из API
    washes = [
        {"id": "1", "name": "АвтоСпа Premium"},
        {"id": "2", "name": "Чистый Кузов"},
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for w in washes:
        buttons.append([InlineKeyboardButton(text=f"🗑 {w['name']}", callback_data=f"del_{w['id']}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text("🗑 <b>Выберите мойку для удаления:</b>", reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("del_"))
async def del_wash_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления"""
    wash_id = callback.data.replace("del_", "")
    
    # TODO: Удаление через API
    
    await callback.message.edit_text(f"✅ Мойка #{wash_id} удалена")
    
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS)
    await callback.message.answer("Главное меню:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # TODO: Получить статистику из API
    stats = {
        "total_washes": 5,
        "total_bookings": 150,
        "bookings_today": 12,
        "revenue_today": 8400,
        "revenue_month": 245000,
        "avg_rating": 4.7
    }
    
    text = f"""
📊 <b>Статистика системы</b>

🏢 Всего моек: {stats['total_washes']}
📅 Всего бронирований: {stats['total_bookings']}

<b>Сегодня:</b>
• Бронирований: {stats['bookings_today']}
• Выручка: {stats['revenue_today']}₽

<b>За месяц:</b>
• Выручка: {stats['revenue_month']}₽

⭐ Средний рейтинг: {stats['avg_rating']}
"""
    
    kb = get_back_keyboard("back_to_menu")
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# ==================== Админ мойки ====================

@router.callback_query(F.data.startswith("wa_today_"))
async def wash_admin_today(callback: CallbackQuery, state: FSMContext):
    """Брони на сегодня для админа мойки"""
    carwash_id = callback.data.replace("wa_today_", "")
    
    # TODO: API запрос
    bookings = [
        {"id": "b1", "time": "10:00", "car": "А123БВ77", "status": "confirmed"},
        {"id": "b2", "time": "11:30", "car": "В456ГД99", "status": "in_progress"},
        {"id": "b3", "time": "14:00", "car": "Е789ЖЗ177", "status": "confirmed"},
    ]
    
    status_icons = {"confirmed": "✅", "in_progress": "🔄", "completed": "✔️"}
    
    lines = ["📋 <b>Брони на сегодня:</b>\n"]
    for b in bookings:
        icon = status_icons.get(b['status'], '❓')
        lines.append(f"{icon} {b['time']} - {b['car']}")
    
    kb = get_back_keyboard("back_to_menu")
    await callback.message.edit_text("\n".join(lines), reply_markup=kb, parse_mode="HTML")
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
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminWashStates.scanning_qr)
async def process_qr_scan(message: Message, state: FSMContext):
    """Обработка QR-кода"""
    qr_code = message.text
    
    # TODO: Проверка QR через API
    # booking = await verify_qr(qr_code)
    
    booking = {
        "id": "b1",
        "guest_name": "Иван Петров",
        "car_plate": "А123БВ77",
        "car_model": "Toyota Camry",
        "wash_type": "Стандарт",
        "status": "confirmed"
    }
    
    if booking:
        text = f"""
✅ <b>QR-код подтверждён!</b>

👤 {booking['guest_name']}
🚗 {booking['car_model']} ({booking['car_plate']})
🧽 {booking['wash_type']}
"""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать мойку", callback_data=f"start_wash_{booking['id']}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
        
        await state.clear()
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer("❌ QR-код не найден или недействителен")


@router.callback_query(F.data.startswith("start_wash_"))
async def start_wash(callback: CallbackQuery, state: FSMContext):
    """Начать мойку"""
    booking_id = callback.data.replace("start_wash_", "")
    
    # TODO: API запрос на обновление статуса
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить мойку", callback_data=f"complete_wash_{booking_id}")],
    ])
    
    await callback.message.edit_text(
        f"🔄 <b>Мойка #{booking_id[:6]} начата</b>\n\n"
        "Нажмите 'Завершить' по окончании работы.",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("complete_wash_"))
async def complete_wash(callback: CallbackQuery, state: FSMContext):
    """Завершить мойку"""
    booking_id = callback.data.replace("complete_wash_", "")
    
    # TODO: API запрос
    
    await callback.message.edit_text(f"✅ <b>Мойка #{booking_id[:6]} завершена!</b>", parse_mode="HTML")
    
    kb = get_main_keyboard(callback.from_user.id, ADMIN_IDS)
    await callback.message.answer("Главное меню:", reply_markup=kb)
    await callback.answer()
