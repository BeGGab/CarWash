"""
Клавиатуры для Telegram бота CarWash
"""

from typing import List
from datetime import date, timedelta

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)


def is_admin(user_id: int, admin_ids: List[int]) -> bool:
    return user_id in admin_ids


def get_main_keyboard(
    user_id: int, admin_ids: List[int] = None, webapp_url: str = None
) -> InlineKeyboardMarkup:
    admin_ids = admin_ids or []
    buttons = []

    if webapp_url:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🚗 Забронировать мойку",
                    web_app=WebAppInfo(url=f"{webapp_url}?action=book"),
                )
            ]
        )
    else:
        buttons.append(
            [InlineKeyboardButton(text="🚗 Найти мойку", callback_data="find_wash")]
        )

    buttons.extend(
        [
            [InlineKeyboardButton(text="📅 Мои брони", callback_data="my_bookings")],
            [
                InlineKeyboardButton(
                    text="📍 Отправить геолокацию", callback_data="send_location"
                )
            ],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        ]
    )

    if is_admin(user_id, admin_ids):
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        text="━━━ Админ-панель ━━━", callback_data="noop"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="➕ Добавить мойку", callback_data="add_wash"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🗑 Удалить мойку", callback_data="del_wash"
                    )
                ],
                [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить местоположение", request_location=True)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_carwashes_keyboard(
    carwashes: List[dict], page: int = 1, total_pages: int = 1
) -> InlineKeyboardMarkup:
    buttons = []
    for cw in carwashes:
        dist = f" ({cw['distance']:.1f} км)" if cw.get("distance") else ""
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🏢 {cw['name']}{dist}", callback_data=f"carwash_{cw['id']}"
                )
            ]
        )

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"cw_page_{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"cw_page_{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append(
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_date_keyboard(carwash_id: str, days_ahead: int = 7) -> InlineKeyboardMarkup:
    buttons, today = [], date.today()
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    row = []

    for i in range(days_ahead):
        d = today + timedelta(days=i)
        text = (
            "Сегодня"
            if i == 0
            else "Завтра"
            if i == 1
            else f"{weekdays[d.weekday()]}, {d.day}"
        )
        row.append(
            InlineKeyboardButton(
                text=text, callback_data=f"date_{carwash_id}_{d.isoformat()}"
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"carwash_{carwash_id}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_slots_keyboard(
    carwash_id: str, slot_date: str, slots: List[dict]
) -> InlineKeyboardMarkup:
    buttons, row = [], []
    for slot in slots:
        row.append(
            InlineKeyboardButton(
                text=f"⏰ {slot['start_time']}", callback_data=f"slot_{slot['id']}"
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if not slots:
        buttons.append(
            [InlineKeyboardButton(text="😔 Нет слотов", callback_data="no_slots")]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔙 Другая дата", callback_data=f"select_date_{carwash_id}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_wash_types_keyboard(
    wash_types: List[dict], slot_id: str
) -> InlineKeyboardMarkup:
    buttons = []
    for wt in wash_types:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{wt['name']} 🕐{wt['duration_minutes']}мин - {wt['base_price']:.0f}₽",
                    callback_data=f"washtype_{slot_id}_{wt['id']}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_slots")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_my_bookings_keyboard(
    bookings: List[dict], show_active: bool = True
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Активные" if show_active else "✅ Активные",
                callback_data="noop" if show_active else "my_bookings",
            ),
            InlineKeyboardButton(
                text="📜 История",
                callback_data="bookings_history" if show_active else "noop",
            ),
        ]
    ]

    icons = {
        "pending_payment": "⏳",
        "confirmed": "✅",
        "in_progress": "🔄",
        "completed": "✔️",
        "cancelled": "❌",
    }
    for b in bookings:
        icon = icons.get(b.get("status", ""), "❓")
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {b.get('car_wash_name', 'Мойка')} - {b.get('slot_date', '')}, {b.get('start_time', '')}",
                    callback_data=f"booking_{b['id']}",
                )
            ]
        )

    if not bookings:
        buttons.append(
            [InlineKeyboardButton(text="У вас нет бронирований", callback_data="noop")]
        )
    buttons.append(
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_booking_detail_keyboard(
    booking: dict, can_cancel: bool = True
) -> InlineKeyboardMarkup:
    buttons, status = [], booking.get("status", "")

    if status == "pending_payment":
        buttons.append(
            [
                InlineKeyboardButton(
                    text="💳 Оплатить", callback_data=f"pay_booking_{booking['id']}"
                )
            ]
        )
    if status == "confirmed":
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📱 Показать QR", callback_data=f"show_qr_{booking['id']}"
                )
            ]
        )
    if can_cancel and status in ["pending_payment", "confirmed"]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Отменить", callback_data=f"cancel_booking_{booking['id']}"
                )
            ]
        )

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text="📍 Как добраться", callback_data=f"navigate_{booking['id']}"
                )
            ],
            [InlineKeyboardButton(text="🔙 К списку", callback_data="my_bookings")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_booking_confirm_keyboard(booking_data: dict) -> InlineKeyboardMarkup:
    prepayment = booking_data.get("final_price", 0) * 0.5
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💳 Оплатить {prepayment:.0f}₽ (50%)",
                    callback_data=f"pay_{booking_data.get('temp_id', 'new')}",
                )
            ],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_booking")],
            [
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data="cancel_booking_flow"
                )
            ],
        ]
    )


def get_confirm_cancel_keyboard(booking_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да", callback_data=f"confirm_cancel_{booking_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет", callback_data=f"booking_{booking_id}"
                ),
            ]
        ]
    )


def get_profile_keyboard(
    is_verified: bool = False, webapp_url: str | None = None
) -> InlineKeyboardMarkup:
    buttons = []
    if not is_verified:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📱 Подтвердить телефон", callback_data="verify_phone"
                )
            ]
        )

    # Если указан webapp_url, используем Mini App для редактирования профиля,
    # иначе остаёмся на callback "edit_profile" как запасной вариант.
    edit_button_kwargs: dict[str, object] = {}
    if webapp_url:
        edit_button_kwargs["web_app"] = WebAppInfo(url=f"{webapp_url}?action=my")
    else:
        edit_button_kwargs["callback_data"] = "edit_profile"

    buttons.extend(
        [
            [InlineKeyboardButton(text="✏️ Редактировать", **edit_button_kwargs)],
            [InlineKeyboardButton(text="🚗 Мои автомобили", callback_data="my_cars")],
            [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )


def get_back_keyboard(callback_data: str = "back_to_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]
        ]
    )
