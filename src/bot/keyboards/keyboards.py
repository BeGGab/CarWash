from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_main_keyboard(user_id):
    if is_admin(user_id):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить мойку", callback_data="add_wash")],
            [InlineKeyboardButton(text="🗑 Удалить мойку", callback_data="del_wash")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton(text="🚗 Забронировать", callback_data="book")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚗 Забронировать", callback_data="book")],
            [InlineKeyboardButton(text="📅 Мои брони", callback_data="my_bookings")]
        ])
