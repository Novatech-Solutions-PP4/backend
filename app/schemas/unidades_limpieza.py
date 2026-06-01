from pydantic import BaseModel
from typing import Optional

class UnidadLimpiezaBase(BaseModel):
    nombre: str

class UnidadLimpiezaCreate(UnidadLimpiezaBase):
    pass

class UnidadLimpiezaUpdate(BaseModel):
    nombre: Optional[str] = None

class UnidadLimpiezaResponse(UnidadLimpiezaBase):
    id: int

    class Config:
        from_attributes = True
