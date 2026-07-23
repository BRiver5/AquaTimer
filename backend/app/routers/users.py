from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_device_id

router = APIRouter(prefix="/users", tags=["users"])


def _get_or_create_user(db: Session, device_id: str) -> models.User:
    user = db.get(models.User, device_id)
    if user is None:
        user = models.User(id=device_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/init", response_model=schemas.UserOut)
def init_user(db: Session = Depends(get_db), device_id: str = Depends(get_device_id)):
    return _get_or_create_user(db, device_id)


@router.get("/me", response_model=schemas.UserOut)
def get_me(db: Session = Depends(get_db), device_id: str = Depends(get_device_id)):
    return _get_or_create_user(db, device_id)


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    patch: schemas.UserUpdate,
    db: Session = Depends(get_db),
    device_id: str = Depends(get_device_id),
):
    user = _get_or_create_user(db, device_id)
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
