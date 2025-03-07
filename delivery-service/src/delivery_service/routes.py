from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Parcel, ParcelType
from .schemas import ParcelCreate, ParcelResponse, ParcelTypeResponse
from starlette.requests import Request
import uuid

router = APIRouter()

@router.post("/parcels/", response_model=ParcelResponse)
def create_parcel(parcel: ParcelCreate, request: Request, db: Session = Depends(get_db)):
    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    db_type = db.query(ParcelType).filter(ParcelType.id == parcel.type_id).first()
    if not db_type:
        raise HTTPException(status_code=400, detail="Invalid parcel type")

    db_parcel = Parcel(
        name=parcel.name,
        weight=parcel.weight,
        type_id=parcel.type_id,
        content_value=parcel.content_value,
        session_id=session_id
    )
    db.add(db_parcel)
    db.commit()
    db.refresh(db_parcel)
    return ParcelResponse(
        id=db_parcel.id,
        name=db_parcel.name,
        weight=db_parcel.weight,
        type_name=db_type.name,
        content_value=db_parcel.content_value,
        delivery_cost="Не рассчитано"
    )

@router.get("/parcel-types/", response_model=list[ParcelTypeResponse])
def get_parcel_types(db: Session = Depends(get_db)):
    return db.query(ParcelType).all()