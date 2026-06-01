from pydantic import BaseModel
from typing import Optional

class ServicioBase(BaseModel):
    nombre: str
    precio: float = 0.0
    baja: bool = False

class ServicioCreate(ServicioBase):
    id_unidad_limpieza: int
    id_modalidad: int

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    baja: Optional[bool] = None

class ServicioResponse(ServicioBase):
    id: int

    class Config:
        from_attributes = True

class ServicioCreate(ServicioBase):
    pass 

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    baja: Optional[bool] = None

class ServicioResponse(ServicioBase):
    id: int

    class Config:
        from_attributes = True