import uuid
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

from datetime import datetime

from src.core.db import Base, uniq_str_an




class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=True)
    username: Mapped[uniq_str_an] = mapped_column(nullable=True)
    email: Mapped[uniq_str_an] = mapped_column(nullable=True)
    first_name: Mapped[uniq_str_an] = mapped_column(nullable=True)
    last_name: Mapped[uniq_str_an] = mapped_column(sa.String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(sa.String, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    last_visit: Mapped[datetime] = mapped_column(default=datetime.now)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now, nullable=True)
    
    bookings: Mapped[List["Booking"]] = relationship(back_populates="user")
    

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"
