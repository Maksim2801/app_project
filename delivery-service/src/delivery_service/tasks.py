from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from .models import Parcel
from .cache import get_exchange_rate

async def calculate_delivery_costs(background_tasks: BackgroundTasks):
    async def task():
        db = next(get_db())
        rate = await get_exchange_rate()
        parcels = db.query(Parcel).filter(Parcel.delivery_cost.is_(None)).all()
        for parcel in parcels:
            cost = (parcel.weight * 0.5 + parcel.content_value * 0.01) * rate
            parcel.delivery_cost = cost
        db.commit()
        db.close()
    background_tasks.add_task(task)