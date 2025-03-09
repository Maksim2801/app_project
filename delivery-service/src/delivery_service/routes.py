from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import get_db
from .models import Parcel, ParcelType
from .schemas import ParcelCreate, ParcelResponse, ParcelTypeResponse, ParcelsQueryParams, SuccessResponse, ErrorResponse
from starlette.requests import Request
from .crud import get_parcels_by_session, get_parcel_by_id
from .tasks import calculate_delivery_costs
import uuid
import logging

logger = logging.getLogger("delivery_service")
router = APIRouter()

@router.post("/parcels/", response_model=SuccessResponse)
def create_parcel(parcel: ParcelCreate, request: Request, db: Session = Depends(get_db)):
    """
    Регистрирует новую посылку.

    Args:
        parcel: Данные посылки (название, вес, тип, стоимость содержимого).
        request: HTTP-запрос для получения сессии пользователя.
        db: Сессия базы данных.

    Returns:
        SuccessResponse: Успешный ответ с данными созданной посылки.

    Raises:
        HTTPException: Если тип посылки недействителен (400).
    """
    logger.info(f"Creating parcel with name: {parcel.name}")
    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    db_type = db.query(ParcelType).filter(ParcelType.id == parcel.type_id).first()
    if not db_type:
        logger.error(f"Invalid parcel type ID: {parcel.type_id}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message="Invalid parcel type").dict()
        )

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
    logger.info(f"Parcel created with ID: {db_parcel.id}")
    response = ParcelResponse(
        id=db_parcel.id,
        name=db_parcel.name,
        weight=db_parcel.weight,
        type_name=db_type.name,
        content_value=db_parcel.content_value,
        delivery_cost="Не рассчитано"
    )
    return SuccessResponse(data=response.dict())

@router.get("/parcel-types/", response_model=SuccessResponse)
def get_parcel_types(db: Session = Depends(get_db)):
    """
    Возвращает список всех типов посылок.

    Args:
        db: Сессия базы данных.

    Returns:
        SuccessResponse: Успешный ответ со списком типов посылок.
    """
    logger.info("Fetching parcel types")
    types = db.query(ParcelType).all()
    logger.info(f"Found {len(types)} parcel types")
    return SuccessResponse(data=[ParcelTypeResponse.from_orm(t).dict() for t in types])

@router.get("/parcels/me/", response_model=SuccessResponse)
def get_user_parcels(request: Request, params: ParcelsQueryParams = Depends(), db: Session = Depends(get_db)):
    """
    Возвращает список посылок текущего пользователя с пагинацией и фильтрацией.

    Args:
        request: HTTP-запрос для получения сессии пользователя.
        params: Параметры пагинации и фильтрации (skip, limit, type_id, has_delivery_cost).
        db: Сессия базы данных.

    Returns:
        SuccessResponse: Успешный ответ со списком посылок.

    Raises:
        HTTPException: Если сессия пользователя не найдена (400).
    """
    session_id = request.session.get("session_id")
    if not session_id:
        logger.error("No session found for request")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message="No session found").dict()
        )
    logger.info(f"Fetching parcels for session: {session_id}")
    parcels = get_parcels_by_session(db, session_id, params.skip, params.limit, params.type_id, params.has_delivery_cost)
    logger.info(f"Found {len(parcels)} parcels for session: {session_id}")
    response = [
        ParcelResponse(
            id=p.id,
            name=p.name,
            weight=p.weight,
            type_name=db.query(ParcelType).filter(ParcelType.id == p.type_id).first().name,
            content_value=p.content_value,
            delivery_cost=str(p.delivery_cost) if p.delivery_cost else "Не рассчитано"
        ) for p in parcels
    ]
    return SuccessResponse(data=[r.dict() for r in response])

@router.get("/parcels/{parcel_id}/", response_model=SuccessResponse)
def get_parcel(parcel_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Возвращает данные о посылке по её ID.

    Args:
        parcel_id: ID посылки.
        request: HTTP-запрос для получения сессии пользователя.
        db: Сессия базы данных.

    Returns:
        SuccessResponse: Успешный ответ с данными посылки.

    Raises:
        HTTPException: Если сессия пользователя не найдена (400) или посылка не найдена/доступ запрещен (404).
    """
    session_id = request.session.get("session_id")
    if not session_id:
        logger.error("No session found for request")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message="No session found").dict()
        )
    logger.info(f"Fetching parcel with ID: {parcel_id} for session: {session_id}")
    parcel = get_parcel_by_id(db, parcel_id, session_id)
    if not parcel:
        logger.error(f"Parcel not found or access denied for ID: {parcel_id}")
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(message="Parcel not found or access denied").dict()
        )
    db_type = db.query(ParcelType).filter(ParcelType.id == parcel.type_id).first()
    logger.info(f"Found parcel with ID: {parcel_id}")
    response = ParcelResponse(
        id=parcel.id,
        name=parcel.name,
        weight=parcel.weight,
        type_name=db_type.name,
        content_value=parcel.content_value,
        delivery_cost=str(parcel.delivery_cost) if parcel.delivery_cost else "Не рассчитано"
    )
    return SuccessResponse(data=response.dict())

@router.get("/calculate-delivery-costs/", response_model=SuccessResponse)
async def trigger_calculation(background_tasks: BackgroundTasks):
    """
    Запускает ручной расчет стоимости доставки для всех необработанных посылок.

    Args:
        background_tasks: Объект для выполнения фоновых задач.

    Returns:
        SuccessResponse: Успешный ответ с подтверждением запуска расчета.
    """
    logger.info("Triggering manual delivery cost calculation")
    await calculate_delivery_costs(background_tasks)
    logger.info("Manual delivery cost calculation triggered")
    return SuccessResponse(data={"message": "Calculation triggered"})