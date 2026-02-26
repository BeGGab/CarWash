"""
Состояния FSM для Telegram бота CarWash
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """Состояния пользователя"""

    # Регистрация
    reg_name = State()
    reg_phone = State()
    waiting_for_phone = State()
    waiting_for_name = State()

    # Бронирование
    selecting_location = State()
    selecting_carwash = State()
    selecting_date = State()
    selecting_time = State()
    selecting_wash_type = State()
    entering_car_info = State()
    entering_car_plate = State()
    entering_car_model = State()
    confirming_booking = State()

    # Управление бронями
    viewing_bookings = State()
    cancelling_booking = State()
    entering_cancel_reason = State()


class AdminWashStates(StatesGroup):
    """Состояния администратора автомойки"""

    # Управление мойкой
    adding_wash_name = State()
    adding_wash_address = State()
    adding_wash_phone = State()
    adding_wash_hours = State()
    adding_wash_location = State()

    # Управление боксами
    adding_bay_number = State()
    adding_bay_type = State()

    # Управление расписанием
    editing_schedule = State()
    blocking_slot = State()

    # Работа с бронями
    scanning_qr = State()
    viewing_booking = State()


class SystemAdminStates(StatesGroup):
    """Состояния системного администратора"""

    # Модерация
    moderating_wash = State()

    # Настройки
    editing_commission = State()

    # Типы мойки
    adding_wash_type_name = State()
    adding_wash_type_desc = State()
    adding_wash_type_duration = State()
    adding_wash_type_price = State()
