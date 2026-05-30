from pydantic import BaseModel
from typing import Optional

class DetalleServicioBase(BaseModel):
    id_pedido: int
    id_servicio: int
    precio_unitario_momento: float

class DetalleServicioCreate(DetalleServicioBase):
    pass

class DetalleServicioUpdate(BaseModel):
    id_pedido: Optional[int] = None
    id_servicio: Optional[int] = None
    precio_unitario_momento: Optional[float] = None

class DetalleServicioResponse(DetalleServicioBase):
    id: int

    class Config:
        from_attributes = True
