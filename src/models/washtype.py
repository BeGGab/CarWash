import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime

from src.core.db import Base, uniq_str_an


class WashType(Base):
    __tablename__ = "wash_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[uniq_str_an]
    description: Mapped[uniq_str_an]
    duration_minutes: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    base_price: Mapped[float] = mapped_column(sa.Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)

    booking: Mapped[List["Booking"]] = relationship(back_populates="wash_type")
