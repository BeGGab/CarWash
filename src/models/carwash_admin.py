import uuid
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class CarWashAdmin(Base):
    __tablename__ = "car_wash_admins"

    id: Mapped[uuid] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True)
    user_name: Mapped[str] = mapped_column(sa.String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    car_wash_id: Mapped[int] = mapped_column(ForeignKey("car_washes.id"))


    user: Mapped["User"] = relationship(back_populates="car_wash_admin_roles")
    car_wash: Mapped["CarWash"] = relationship(back_populates="admins")

    def __repr__(self) -> str:
        return f"<CarWashAdmin(user_id={self.user_id}, car_wash_id={self.car_wash_id})>"

