from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .database import Base

class ParcelType(Base):
    __tablename__ = "parcel_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)

class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("parcel_types.id"), nullable=False)
    content_value = Column(Float, nullable=False)  # В долларах
    delivery_cost = Column(Float, nullable=True)   # В рублях
    session_id = Column(String(100), nullable=False)  # ID сессии