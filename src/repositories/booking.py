import uuid
import base64
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking
from src.models.carwash import CarWash
from src.models.timeslot import TimeSlot
from src.models.washtype import WashType
from src.schemas.booking import SBookingCreate


class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def statistic_total(self, id: uuid.UUID) -> int:
        query = select(func.count(Booking.id)).where(Booking.user_id == id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def statistic_completed(self, id: uuid.UUID) -> int:
        query = select(func.count(Booking.id)).where(
            Booking.user_id == id, Booking.status == "completed"
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_available_slot(self, time_slot_id: uuid.UUID) -> Optional[TimeSlot]:
        slot_query = (
            select(TimeSlot)
            .where(TimeSlot.id == time_slot_id, TimeSlot.status == "available")
            .options(selectinload(TimeSlot.wash_bay))
        )
        slot_result = await self.session.execute(slot_query)
        return slot_result.scalar_one_or_none()

    async def get_carwash(self, car_wash_id: uuid.UUID) -> Optional[CarWash]:
        cw_query = select(CarWash).where(CarWash.id == car_wash_id)
        cw_result = await self.session.execute(cw_query)
        return cw_result.scalar_one_or_none()

    async def get_wash_type(self, wash_type_id: uuid.UUID) -> Optional[WashType]:
        wt_query = select(WashType).where(WashType.id == wash_type_id)
        wt_result = await self.session.execute(wt_query)
        return wt_result.scalar_one_or_none()

    @staticmethod
    def calculate_price(wash_type: WashType, discount: float = 0) -> tuple[float, float, float]:
        """Расчет цены с учетом скидки"""
        price = wash_type.base_price
        discount_amount = price * (discount / 100)
        final_price = price - discount_amount
        return price, discount_amount, final_price

    @staticmethod
    def generate_qr_data(booking_id: uuid.UUID, user_phone: str) -> str:
        data = f"{booking_id}:{user_phone}:{datetime.now().isoformat()}"
        hash_obj = hashlib.sha256(data.encode())
        return base64.urlsafe_b64encode(hash_obj.digest()[:16]).decode()

    async def create_booking(self, data: SBookingCreate) -> tuple[Booking, TimeSlot, CarWash, WashType]:
        # 1. Проверяем доступность слота
        slot = await self.get_available_slot(data.time_slot_id)
        if not slot:
            raise HTTPException(status_code=400, detail="Слот недоступен или уже забронирован")

        # 2. Проверяем автомойку
        carwash = await self.get_carwash(data.car_wash_id)
        if not carwash:
            raise HTTPException(status_code=404, detail="Автомойка не найдена")

        # 3. Получаем тип мойки
        wash_type = await self.get_wash_type(data.wash_type_id)
        if not wash_type:
            raise HTTPException(status_code=404, detail="Тип мойки не найден")

        # 4. Рассчитываем цену
        price, discount_amount, final_price = self.calculate_price(wash_type, 0) # Скидка пока 0

        # 5. Создаем бронирование
        booking = Booking(
            car_wash_id=data.car_wash_id,
            wash_bay_id=slot.wash_bay_id,
            time_slot_id=data.time_slot_id,
            wash_type_id=data.wash_type_id,
            guest_phone=data.guest_phone,
            guest_name=data.guest_name,
            car_plate=data.car_plate.upper(),
            car_model=data.car_model,
            slot_date=slot.slot_date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            duration_minutes=wash_type.duration_minutes,
            price=price,
            discount=discount_amount,
            final_price=final_price,
            status="pending_payment",
            payment_status="pending",
            expires_at=datetime.now() + timedelta(minutes=15),  # 15 минут на оплату
            notes=data.notes
        )
        self.session.add(booking)

        # 6. Блокируем слот
        slot.status = "reserved"

        # 7. Сохраняем изменения в БД
        await self.session.flush()
        await self.session.refresh(booking)

        return booking, slot, carwash, wash_type

    async def get_by_phone(
        self,
        phone: str,
        status: Optional[str],
        page: int,
        per_page: int,
    ) -> tuple[List[Booking], int]:
        """Получает бронирования по номеру телефона с пагинацией."""
        # Базовый запрос для фильтрации
        base_query = select(Booking).where(Booking.guest_phone == phone)
        if status:
            base_query = base_query.where(Booking.status == status)

        # Запрос для подсчета общего количества
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Основной запрос для получения данных
        offset = (page - 1) * per_page
        data_query = (
            base_query.order_by(Booking.slot_date.desc(), Booking.start_time.desc())
            .offset(offset)
            .limit(per_page)
            .options(
                selectinload(Booking.car_wash),
                selectinload(Booking.wash_type),
                selectinload(Booking.wash_bay),
            )
        )

        result = await self.session.execute(data_query)
        bookings = result.scalars().all()

        return bookings, total

    async def get_by_id(self, booking_id: uuid.UUID) -> Optional[Booking]:
        """Получает бронирование по ID с загрузкой связей."""
        query = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                selectinload(Booking.car_wash),
                selectinload(Booking.wash_type),
                selectinload(Booking.wash_bay),
                selectinload(Booking.time_slot),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_for_carwash(
        self,
        carwash_id: uuid.UUID,
        date_from: Optional[datetime.date],
        date_to: Optional[datetime.date],
        status: Optional[str],
        page: int,
        per_page: int,
    ) -> tuple[List[Booking], int]:
        """Получает бронирования для конкретной автомойки с фильтрами и пагинацией."""
        base_query = select(Booking).where(Booking.car_wash_id == carwash_id)

        if date_from:
            base_query = base_query.where(Booking.slot_date >= date_from)
        if date_to:
            base_query = base_query.where(Booking.slot_date <= date_to)
        if status:
            base_query = base_query.where(Booking.status == status)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * per_page
        data_query = (
            base_query.order_by(Booking.slot_date, Booking.start_time)
            .offset(offset)
            .limit(per_page)
            .options(selectinload(Booking.wash_type), selectinload(Booking.wash_bay))
        )

        result = await self.session.execute(data_query)
        bookings = result.scalars().all()

        return bookings, total

    async def update_status(
        self, booking: Booking, new_status: str, completed_at: Optional[datetime] = None
    ) -> Booking:
        """Обновляет статус бронирования."""
        booking.status = new_status
        if completed_at:
            booking.completed_at = completed_at
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def update_payment_info(self, booking: Booking, payment_id: str) -> Booking:
        """Обновляет информацию о платеже в бронировании."""
        booking.payment_id = payment_id
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def find_pending_payment(self) -> Optional[Booking]:
        """Находит последнее бронирование, ожидающее оплаты."""
        query = (
            select(Booking)
            .where(Booking.payment_status == "pending")
            .order_by(Booking.created_at.desc())
            .options(selectinload(Booking.time_slot))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()