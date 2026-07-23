from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Units = Literal["ml", "fl_oz"]
ContainerType = Literal["glass", "bottle", "mug", "cup"]
AccentColor = Literal["teal", "blue", "cyan", "green", "indigo", "sky"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    daily_goal_ml: int
    weight_kg: float | None
    units: Units
    accent_color: AccentColor
    container_type: ContainerType
    reminders_master_enabled: bool
    welcome_dismissed: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    daily_goal_ml: int | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    units: Units | None = None
    accent_color: AccentColor | None = None
    container_type: ContainerType | None = None
    reminders_master_enabled: bool | None = None
    welcome_dismissed: bool | None = None


class IntakeIn(BaseModel):
    amount_ml: int = Field(gt=0)
    logged_at: datetime | None = None


class IntakeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount_ml: int
    logged_at: datetime


class DayTotalOut(BaseModel):
    date: str
    total_ml: int
    goal_ml: int
    goal_met: bool


class StatsOut(BaseModel):
    average_daily_ml: int
    best_streak_days: int
    total_days_tracked: int


class ReminderIn(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    enabled: bool = True


class ReminderUpdate(BaseModel):
    hour: int | None = Field(default=None, ge=0, le=23)
    minute: int | None = Field(default=None, ge=0, le=59)
    enabled: bool | None = None
    notification_identifier: str | None = None


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hour: int
    minute: int
    enabled: bool
    notification_identifier: str | None
