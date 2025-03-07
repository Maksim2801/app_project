from fastapi import FastAPI
from .routes import router
from .database import engine, Base
from fastapi_sessions import SessionMiddleware

app = FastAPI(title="Delivery Service API")
app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.include_router(router)

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