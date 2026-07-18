from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.feeding import Feeding
from app.models.starter import Starter
from app.schemas.starter import FeedingCreate, FeedingOut, StarterCreate, StarterOut, StarterUpdate

router = APIRouter(prefix="/starters", tags=["starters"])


@router.get("/", response_model=list[StarterOut])
def list_starters(show_archived: bool = Query(False), db: Session = Depends(get_db)):
    q = db.query(Starter)
    if not show_archived:
        q = q.filter(Starter.archived.is_(False))
    return q.all()


@router.post("/", response_model=StarterOut, status_code=201)
def create_starter(body: StarterCreate, db: Session = Depends(get_db)):
    starter = Starter(**body.model_dump())
    db.add(starter)
    db.commit()
    db.refresh(starter)
    return starter


@router.get("/{starter_id}", response_model=StarterOut)
def get_starter(starter_id: int, db: Session = Depends(get_db)):
    starter = db.get(Starter, starter_id)
    if not starter:
        raise HTTPException(status_code=404, detail="Starter not found")
    return starter


@router.patch("/{starter_id}", response_model=StarterOut)
def update_starter(starter_id: int, body: StarterUpdate, db: Session = Depends(get_db)):
    starter = db.get(Starter, starter_id)
    if not starter:
        raise HTTPException(status_code=404, detail="Starter not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(starter, field, value)
    db.commit()
    db.refresh(starter)
    return starter


@router.delete("/{starter_id}", status_code=204)
def delete_starter(starter_id: int, db: Session = Depends(get_db)):
    starter = db.get(Starter, starter_id)
    if not starter:
        raise HTTPException(status_code=404, detail="Starter not found")
    db.delete(starter)
    db.commit()


@router.post("/{starter_id}/feedings", response_model=FeedingOut, status_code=201)
def add_feeding(starter_id: int, body: FeedingCreate, db: Session = Depends(get_db)):
    if not db.get(Starter, starter_id):
        raise HTTPException(status_code=404, detail="Starter not found")
    feeding = Feeding(starter_id=starter_id, fed_at=datetime.now(timezone.utc), **body.model_dump())
    db.add(feeding)
    db.commit()
    db.refresh(feeding)
    return feeding


@router.get("/{starter_id}/feedings", response_model=list[FeedingOut])
def list_feedings(starter_id: int, db: Session = Depends(get_db)):
    if not db.get(Starter, starter_id):
        raise HTTPException(status_code=404, detail="Starter not found")
    return db.query(Feeding).filter(Feeding.starter_id == starter_id).all()
