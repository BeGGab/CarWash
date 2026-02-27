import uuid
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class CarWashAdmin(Base):
    __tablename__ = "car_wash_admins"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_name: Mapped[str] = mapped_column(sa.String, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    car_wash_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("car_washes.id"))

    user: Mapped["User"] = relationship(back_populates="car_wash_admin_roles")
    car_wash: Mapped["CarWash"] = relationship(back_populates="admins")

    def __repr__(self) -> str:
        return f"<CarWashAdmin(user_id={self.user_id}, car_wash_id={self.car_wash_id})>"
