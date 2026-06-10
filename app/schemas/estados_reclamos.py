from pydantic import BaseModel
from typing import Optional

class EstadoReclamoBase(BaseModel):
    nombre: str

class EstadoReclamoCreate(EstadoReclamoBase):
    pass

class EstadoReclamoUpdate(BaseModel):
    nombre: Optional[str] = None

class EstadoReclamoResponse(EstadoReclamoBase):
    id: int

    class Config:
        from_attributes = True