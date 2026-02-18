import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime

from src.core.db import Base, uniq_str_an


metadata = sa.MetaData()


class WashBay(Base):
    __tablename__ = "wash_bays"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    car_wash_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("car_washes.id"))
    bay_number: Mapped[int]
    bay_type: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)

    car_wash: Mapped["CarWash"] = relationship(back_populates="bays")
    time_slots: Mapped[List["TimeSlot"]] = relationship(
        back_populates="wash_bay", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="wash_bay")
    
