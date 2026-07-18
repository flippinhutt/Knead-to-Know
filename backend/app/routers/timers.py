from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.timer import Timer
from app.schemas.timer import TimerCreate, TimerOut

router = APIRouter(prefix="/timers", tags=["timers"])


@router.get("/", response_model=list[TimerOut])
def list_timers(db: Session = Depends(get_db)):
    return db.query(Timer).all()


@router.post("/", response_model=TimerOut, status_code=201)
def create_timer(body: TimerCreate, db: Session = Depends(get_db)):
    timer = Timer(**body.model_dump())
    db.add(timer)
    db.commit()
    db.refresh(timer)
    return timer


@router.get("/{timer_id}", response_model=TimerOut)
def get_timer(timer_id: int, db: Session = Depends(get_db)):
    timer = db.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    return timer


@router.post("/{timer_id}/start", response_model=TimerOut)
def start_timer(timer_id: int, db: Session = Depends(get_db)):
    timer = db.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    now = datetime.now(timezone.utc)
    timer.started_at = now
    timer.ends_at = now + timedelta(minutes=timer.duration_minutes)
    timer.is_active = True
    db.commit()
    db.refresh(timer)
    return timer


@router.post("/{timer_id}/stop", response_model=TimerOut)
def stop_timer(timer_id: int, db: Session = Depends(get_db)):
    timer = db.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    timer.is_active = False
    db.commit()
    db.refresh(timer)
    return timer


@router.delete("/{timer_id}", status_code=204)
def delete_timer(timer_id: int, db: Session = Depends(get_db)):
    timer = db.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    db.delete(timer)
    db.commit()
