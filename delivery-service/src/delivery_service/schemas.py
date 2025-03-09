from pydantic import BaseModel, Field
from typing import Any

class ParcelCreate(BaseModel):
    name: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0)
    type_id: int = Field(..., ge=1, le=3)
    content_value: float = Field(..., ge=0)

class ParcelResponse(BaseModel):
    id: int
    name: str
    weight: float
    type_name: str
    content_value: float
    delivery_cost: str

    class Config:
        from_attributes = True

class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ParcelsQueryParams(BaseModel):
    skip: int = 0
    limit: int = 10
    type_id: int = None
    has_delivery_cost: bool = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any