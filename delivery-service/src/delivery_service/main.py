from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .routes import router
from .database import engine, Base
from .tasks import calculate_delivery_costs
from .logs import setup_logging
import asyncio

app = FastAPI(title="Delivery Service API")
app.add_middleware(SessionMiddleware, secret_key="my-super-secret-key-12345")
app.include_router(router)

# Инициализация логирования
logger = setup_logging()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .models import ParcelType
    db = SessionLocal()
    if not db.query(ParcelType).first():
        types = [
            ParcelType(id=1, name="одежда"),
            ParcelType(id=2, name="электроника"),
            ParcelType(id=3, name="разное")
        ]
        db.add_all(types)
        db.commit()
    db.close()

    logger.info("Application started, database initialized")

    # Периодический запуск каждые 5 минут
    async def periodic_task():
        while True:
            logger.info("Starting delivery cost calculation")
            await calculate_delivery_costs(BackgroundTasks())
            logger.info("Delivery cost calculation completed")
            await asyncio.sleep(300)

    asyncio.create_task(periodic_task())