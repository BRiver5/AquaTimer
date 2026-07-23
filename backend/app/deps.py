from fastapi import Header, HTTPException

from .database import get_db as get_db  # re-exported for convenient single-import in routers


def get_device_id(x_device_id: str | None = Header(default=None)) -> str:
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing required X-Device-Id header")
    return x_device_id
