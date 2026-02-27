import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime

from src.core.db import Base, uniq_str_an


class CarWash(Base):
    __tablename__ = "car_washes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[uniq_str_an]
    address: Mapped[uniq_str_an]
    phone_number: Mapped[uniq_str_an]
    working_hours: Mapped[dict] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)

    bays: Mapped[List["WashBay"]] = relationship(
        back_populates="car_wash", cascade="all, delete-orphan"
    )
    time_slots: Mapped[List["TimeSlot"]] = relationship(
        back_populates="car_wash", cascade="all, delete-orphan"
    )
    booking: Mapped[List["Booking"]] = relationship(back_populates="car_wash")
    
    admins: Mapped[List["CarWashAdmin"]] = relationship(back_populates="car_wash", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CarWash(name={self.name}, address={self.address})>"



