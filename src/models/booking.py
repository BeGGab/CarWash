import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime

from src.core.db import Base, uniq_str_an


metadata = sa.MetaData()


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    car_wash_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("car_washes.id", ondelete="CASCADE"), nullable=False)
    wash_bay_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("wash_bays.id", ondelete="CASCADE"), nullable=False)
    time_slot_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("time_slots.id", ondelete="CASCADE"), nullable=False)
    wash_type_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("wash_types.id"), nullable=False)

    guest_phone: Mapped[str]
    guest_name: Mapped[str]

    car_plate: Mapped[str]
    car_model: Mapped[str]

    booking_date: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    slot_date: Mapped[datetime] = mapped_column(sa.Date, nullable=False)
    start_time: Mapped[datetime] = mapped_column(sa.Time, nullable=False)
    end_time: Mapped[datetime] = mapped_column(sa.Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(sa.Integer, nullable=False)


    price: Mapped[float] = mapped_column(sa.Float, nullable=False)
    discount: Mapped[float] = mapped_column(sa.Float, default=0)
    final_price: Mapped[float] = mapped_column(sa.Float, nullable=False)

    status: Mapped[str] = mapped_column(default="confirmed")
    payment_status: Mapped[str] = mapped_column(default="pending")

    expires_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)

    notes: Mapped[str] = mapped_column(nullable=True)
    cancellation_reason: Mapped[str] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="booking")
    car_wash: Mapped["CarWash"] = relationship(back_populates="booking")
    wash_bay: Mapped["WashBay"] = relationship(back_populates="bookings")
    time_slot: Mapped["TimeSlot"] = relationship(back_populates="booking")
    wash_type: Mapped["WashType"] = relationship(back_populates="booking")