from pydantic import BaseModel
from typing import Optional

class ModalidadServicioBase(BaseModel):
    nombre: str

class ModalidadServicioCreate(ModalidadServicioBase):
    pass

class ModalidadServicioUpdate(BaseModel):
    nombre: Optional[str] = None

class ModalidadServicioResponse(ModalidadServicioBase):
    id: int

    class Config:
        from_attributes = True
