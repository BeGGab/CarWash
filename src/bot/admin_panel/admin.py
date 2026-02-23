import logging
from aiogram import Bot, Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from src.schemas.carwash import SCarWashCreate
from src.services.carwash import (
    create_carwash_service,
    get_all_carwashes_service,
    delete_carwash_service,
    get_statistics_service,
)


admin_router = Router()


class AdminStates(StatesGroup):
    add_wash_name = State()


@admin_router.message(Command("start"))
async def cmd_start(msg: types.Message):
    # TODO: Заменить на реальную клавиатуру
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Админ-панель", callback_data="admin_menu")]
        ]
    )
    await msg.answer("🚿 Добро пожаловать в систему бронирования!", reply_markup=kb)


async def get_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить мойку", callback_data="add_wash")],
            [InlineKeyboardButton(text="➖ Удалить мойку", callback_data="del_wash")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        ]
    )


# Для Админа: добавить мойку
@admin_router.callback_query(lambda c: c.data == "add_wash")
async def add_wash_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📝 Введите название мойки:")
    await state.set_state(AdminStates.add_wash_name)
    await call.answer()


@admin_router.message(AdminStates.add_wash_name)
async def add_wash_done(msg: types.Message, state: FSMContext, session: AsyncSession):
    try:
        data = SCarWashCreate(name=msg.text, address="Не указан", location="0,0")
        await create_carwash_service(data, session)
        await msg.answer(f"✅ Мойка '{msg.text}' добавлена.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении мойки: {e}")
        await msg.answer(f"❌ Ошибка: {e}")

    await state.clear()
    await msg.answer("Админ-панель:", reply_markup=await get_admin_keyboard())


# Для Админа: удалить мойку
@admin_router.callback_query(lambda c: c.data == "del_wash")
async def del_wash_start(call: types.CallbackQuery, session: AsyncSession):
    washes = await get_all_carwashes_service(session)
    if not washes:
        await call.message.answer("❌ Нет моек для удаления")
        return await call.answer()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=w.name, callback_data=f"del_{w.id}")]
            for w in washes
        ]
        + [[InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]]
    )
    await call.message.answer("Выберите мойку для удаления:", reply_markup=kb)
    await call.answer()


@admin_router.callback_query(lambda c: c.data.startswith("del_"))
async def del_wash_done(call: types.CallbackQuery, session: AsyncSession):
    wash_id = call.data.split("_")[1]
    await delete_carwash_service(wash_id, session)
    await call.message.answer("✅ Мойка удалена")
    await call.message.answer("Админ-панель:", reply_markup=await get_admin_keyboard())
    await call.answer()


#  Статистика
@admin_router.callback_query(lambda c: c.data == "stats")
async def show_stats(call: types.CallbackQuery, session: AsyncSession):
    stats = await get_statistics_service(session)
    percent = (
        (stats["confirmed_bookings"] / stats["total_bookings"] * 100)
        if stats["total_bookings"] > 0
        else 0
    )

    text = f"""📊 Статистика:
🏢 Всего моек: {stats["carwashes_count"]}
📅 Всего бронирований: {stats["total_bookings"]}
✅ Подтверждено: {stats["confirmed_bookings"]} ({percent:.1f}%)"""

    await call.message.answer(text)
    await call.answer()
