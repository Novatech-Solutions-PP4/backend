from pydantic import BaseModel, field_validator
from typing import Optional

class InsumoBase(BaseModel):
    nombre: str
    cantidad: float = 0.0
    cantidad_alerta: float = 0.0
    costo_actual: float = 0.0

    @field_validator("cantidad_alerta", "costo_actual")
    @classmethod
    def validar_no_negativo(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError("El valor no puede ser negativo.")
        return v

class InsumoCreate(InsumoBase):
    pass 

class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    cantidad: Optional[float] = None
    cantidad_alerta: Optional[float] = None
    costo_actual: Optional[float] = None
    baja: Optional[bool] = None

class InsumoResponse(InsumoBase):
    id: int
    baja: bool

    class Config:
        from_attributes = True