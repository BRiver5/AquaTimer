from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_device_id
from .users import _get_or_create_user

router = APIRouter(prefix="/intake", tags=["intake"])


def _day_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


@router.post("", response_model=schemas.IntakeOut)
def add_intake(
    payload: schemas.IntakeIn,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    _get_or_create_user(db, device_id)
    entry = models.IntakeEntry(
        user_id=device_id,
        amount_ml=payload.amount_ml,
        logged_at=payload.logged_at or datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/today", response_model=list[schemas.IntakeOut])
def get_today_intake(
    range_start: datetime,
    range_end: datetime,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    return (
        db.query(models.IntakeEntry)
        .filter(
            models.IntakeEntry.user_id == device_id,
            models.IntakeEntry.logged_at >= range_start,
            models.IntakeEntry.logged_at < range_end,
        )
        .order_by(models.IntakeEntry.logged_at.asc())
        .all()
    )


@router.delete("/{entry_id}", status_code=204)
def delete_intake(
    entry_id: int,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    entry = (
        db.query(models.IntakeEntry)
        .filter(models.IntakeEntry.id == entry_id, models.IntakeEntry.user_id == device_id)
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Intake entry not found")
    db.delete(entry)
    db.commit()


@router.delete("", status_code=204)
def clear_all_intake(db: Session = Depends(get_db), device_id: str = Depends(get_device_id)):
    """Bulk-delete, added beyond the original per-id DELETE /intake/{id} spec so the
    mobile app's "Clear all history" action has an exact REST-mode equivalent to
    LocalRepository.clearAllHistory()."""
    db.query(models.IntakeEntry).filter(models.IntakeEntry.user_id == device_id).delete()
    db.commit()


@router.get("/weekly", response_model=list[schemas.DayTotalOut])
def get_weekly_totals(
    range_start: datetime,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    user = _get_or_create_user(db, device_id)
    range_end = range_start + timedelta(days=7)

    rows = (
        db.query(models.IntakeEntry)
        .filter(
            models.IntakeEntry.user_id == device_id,
            models.IntakeEntry.logged_at >= range_start,
            models.IntakeEntry.logged_at < range_end,
        )
        .all()
    )

    totals: dict[str, int] = {}
    for row in rows:
        key = _day_key(row.logged_at)
        totals[key] = totals.get(key, 0) + row.amount_ml

    result = []
    for offset in range(7):
        day = range_start + timedelta(days=offset)
        key = _day_key(day)
        total_ml = totals.get(key, 0)
        result.append(
            schemas.DayTotalOut(
                date=key,
                total_ml=total_ml,
                goal_ml=user.daily_goal_ml,
                goal_met=total_ml >= user.daily_goal_ml,
            )
        )
    return result


@router.get("/stats", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db), device_id: str = Depends(get_device_id)):
    user = _get_or_create_user(db, device_id)

    day_totals_query = (
        db.query(
            func.date(models.IntakeEntry.logged_at).label("day"),
            func.sum(models.IntakeEntry.amount_ml).label("total_ml"),
        )
        .filter(models.IntakeEntry.user_id == device_id)
        .group_by("day")
        .order_by("day")
        .all()
    )

    total_days_tracked = len(day_totals_query)
    average_daily_ml = (
        round(sum(row.total_ml for row in day_totals_query) / total_days_tracked)
        if total_days_tracked > 0
        else 0
    )

    best_streak = 0
    current_streak = 0
    prev_day: datetime | None = None
    for row in day_totals_query:
        day = datetime.strptime(row.day, "%Y-%m-%d")
        is_consecutive = prev_day is not None and (day - prev_day).days == 1
        if row.total_ml >= user.daily_goal_ml:
            current_streak = current_streak + 1 if is_consecutive else 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0
        prev_day = day

    return schemas.StatsOut(
        average_daily_ml=average_daily_ml,
        best_streak_days=best_streak,
        total_days_tracked=total_days_tracked,
    )
