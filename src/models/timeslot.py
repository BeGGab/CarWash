import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime

from src.core.db import Base, uniq_str_an


metadata = sa.MetaData()


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    car_wash_id: Mapped[int] = mapped_column(sa.ForeignKey("car_washes.id"))
    wash_bay_id: Mapped[int] = mapped_column(sa.ForeignKey("wash_bays.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    slot_date: Mapped[datetime]
    status: Mapped[str] = mapped_column(default="available")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)

    car_wash: Mapped["CarWash"] = relationship(back_populates="time_slots")
    wash_bay: Mapped["WashBay"] = relationship(back_populates="time_slots")
    booking: Mapped["Booking"] = relationship(back_populates="time_slot", uselist=False)
    