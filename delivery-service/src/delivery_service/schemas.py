from pydantic import BaseModel, Field

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
    delivery_cost: str  # "Не рассчитано" или значение

    class Config:
        orm_mode = True

class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True