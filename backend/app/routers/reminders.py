from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_device_id
from .users import _get_or_create_user

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("", response_model=list[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db), device_id: str = Depends(get_device_id)):
    return (
        db.query(models.Reminder)
        .filter(models.Reminder.user_id == device_id)
        .order_by(models.Reminder.hour.asc(), models.Reminder.minute.asc())
        .all()
    )


@router.post("", response_model=schemas.ReminderOut)
def create_reminder(
    payload: schemas.ReminderIn,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    _get_or_create_user(db, device_id)
    reminder = models.Reminder(
        user_id=device_id, hour=payload.hour, minute=payload.minute, enabled=payload.enabled
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def _get_owned_reminder(db: Session, device_id: str, reminder_id: int) -> models.Reminder:
    reminder = (
        db.query(models.Reminder)
        .filter(models.Reminder.id == reminder_id, models.Reminder.user_id == device_id)
        .first()
    )
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.put("/{reminder_id}", response_model=schemas.ReminderOut)
def update_reminder(
    reminder_id: int,
    patch: schemas.ReminderUpdate,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    reminder = _get_owned_reminder(db, device_id, reminder_id)
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    reminder = _get_owned_reminder(db, device_id, reminder_id)
    db.delete(reminder)
    db.commit()
