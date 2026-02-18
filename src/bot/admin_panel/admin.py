import asyncio
import logging
import aiosqlite
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = await get_main_keyboard(msg.from_user.id)
    await msg.answer("🚿 Добро пожаловать в систему бронирования!", reply_markup=kb)

# --- Админ: добавить мойку ---
@dp.callback_query(lambda c: c.data == "add_wash")
async def add_wash_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📝 Введите название мойки:")
    await state.set_state(States.add_wash)
    await call.answer()

@dp.message(States.add_wash)
async def add_wash_done(msg: types.Message, state: FSMContext):
    try:
        await db_query("INSERT INTO car_washes(name) VALUES (?)", (msg.text,))
        wash = await db_query("SELECT id FROM car_washes WHERE name=?", (msg.text,), fetch_one=True)
        if wash:
            await create_slots_for_wash(wash[0])  # Автоматически создаем слоты на 30 дней
        await msg.answer(f"✅ Мойка '{msg.text}' добавлена\nСозданы слоты на 30 дней вперед")
    except:
        await msg.answer("❌ Такая мойка уже есть")
    
    await state.clear()
    kb = await get_main_keyboard(msg.from_user.id)
    await msg.answer("Главное меню:", reply_markup=kb)

# --- Админ: удалить мойку ---
@dp.callback_query(lambda c: c.data == "del_wash")
async def del_wash_start(call: types.CallbackQuery):
    washes = await db_query("SELECT id, name FROM car_washes", fetch_all=True)
    if not washes:
        await call.message.answer("❌ Нет моек для удаления")
        return await call.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"del_{id}")] for id, name in washes
    ] + [[InlineKeyboardButton(text="🔙 Назад", callback_data="back")]])
    await call.message.answer("Выберите мойку для удаления:", reply_markup=kb)
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("del_"))
async def del_wash_done(call: types.CallbackQuery):
    wash_id = int(call.data.split("_")[1])
    await db_query("DELETE FROM car_washes WHERE id=?", (wash_id,))
    await call.message.answer("✅ Мойка удалена")
    kb = await get_main_keyboard(call.from_user.id)
    await call.message.answer("Главное меню:", reply_markup=kb)
    await call.answer()

# --- Статистика ---
@dp.callback_query(lambda c: c.data == "stats")
async def show_stats(call: types.CallbackQuery):
    washes = await db_query("SELECT COUNT(*) FROM car_washes", fetch_one=True)
    total = await db_query("SELECT COUNT(*) FROM slots", fetch_one=True)
    booked = await db_query("SELECT COUNT(*) FROM slots WHERE user_id IS NOT NULL", fetch_one=True)
    
    washes = washes[0] if washes else 0
    total = total[0] if total else 0
    booked = booked[0] if booked else 0
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_slots = await db_query("SELECT COUNT(*) FROM slots WHERE date=?", (today,), fetch_one=True)
    today_booked = await db_query("SELECT COUNT(*) FROM slots WHERE date=? AND user_id IS NOT NULL", 
                                 (today,), fetch_one=True)
    
    today_slots = today_slots[0] if today_slots else 0
    today_booked = today_booked[0] if today_booked else 0
    percent = (booked/total*100) if total > 0 else 0
    
    text = f"""📊 Статистика:
🏢 Моек: {washes}
📅 Всего слотов: {total}
✅ Занято: {booked} ({percent:.1f}%)
📅 Сегодня: {today_slots} слотов, {today_booked} занято"""
    
    await call.message.answer(text)
    await call.answer()
