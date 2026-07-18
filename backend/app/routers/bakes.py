from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.bake import Bake
from app.schemas.bake import BakeCreate, BakeOut

router = APIRouter(prefix="/bakes", tags=["bakes"])


@router.get("/", response_model=list[BakeOut])
def list_bakes(db: Session = Depends(get_db)):
    return db.query(Bake).order_by(Bake.baked_at.desc()).all()


@router.post("/", response_model=BakeOut, status_code=201)
def create_bake(body: BakeCreate, db: Session = Depends(get_db)):
    bake = Bake(**body.model_dump())
    db.add(bake)
    db.commit()
    db.refresh(bake)
    return bake


@router.get("/{bake_id}", response_model=BakeOut)
def get_bake(bake_id: int, db: Session = Depends(get_db)):
    bake = db.get(Bake, bake_id)
    if not bake:
        raise HTTPException(status_code=404, detail="Bake not found")
    return bake


@router.delete("/{bake_id}", status_code=204)
def delete_bake(bake_id: int, db: Session = Depends(get_db)):
    bake = db.get(Bake, bake_id)
    if not bake:
        raise HTTPException(status_code=404, detail="Bake not found")
    db.delete(bake)
    db.commit()
