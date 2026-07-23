from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Anonymous per-device profile, keyed by the client-generated device UUID."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    daily_goal_ml: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    units: Mapped[str] = mapped_column(String, nullable=False, default="ml")
    accent_color: Mapped[str] = mapped_column(String, nullable=False, default="teal")
    container_type: Mapped[str] = mapped_column(String, nullable=False, default="glass")
    reminders_master_enabled: Mapped[bool] = mapped_column(default=True)
    welcome_dismissed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    intake_entries: Mapped[list["IntakeEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("units IN ('ml','fl_oz')", name="ck_users_units"),
        CheckConstraint("container_type IN ('glass','bottle','mug','cup')", name="ck_users_container_type"),
    )


class IntakeEntry(Base):
    __tablename__ = "intake_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="intake_entries")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True)
    notification_identifier: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="reminders")

    __table_args__ = (
        CheckConstraint("hour BETWEEN 0 AND 23", name="ck_reminders_hour"),
        CheckConstraint("minute BETWEEN 0 AND 59", name="ck_reminders_minute"),
    )
