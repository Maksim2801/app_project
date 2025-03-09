from sqlalchemy.orm import Session
from .models import Parcel, ParcelType
from .schemas import ParcelResponse

def get_parcels_by_session(db: Session, session_id: str, skip: int = 0, limit: int = 10, type_id: int = None, has_delivery_cost: bool = None):
    query = db.query(Parcel).join(ParcelType).filter(Parcel.session_id == session_id)
    if type_id:
        query = query.filter(Parcel.type_id == type_id)
    if has_delivery_cost is not None:
        query = query.filter(Parcel.delivery_cost.isnot(None) if has_delivery_cost else Parcel.delivery_cost.is_(None))
    return query.offset(skip).limit(limit).all()

def get_parcel_by_id(db: Session, parcel_id: int, session_id: str):
    parcel = db.query(Parcel).join(ParcelType).filter(Parcel.id == parcel_id, Parcel.session_id == session_id).first()
    if not parcel:
        return None
    return parcel