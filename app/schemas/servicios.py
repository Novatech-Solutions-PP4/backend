from pydantic import BaseModel, field_validator
from typing import Optional, List
from app.schemas.unidades_limpieza import UnidadLimpiezaResponse
from app.schemas.modalidades_servicio import ModalidadServicioResponse

class InsumoServicioDetalle(BaseModel):
    id: int
    nombre: str
    class Config: from_attributes = True

class InsumoServicioBase(BaseModel):
    id_insumo: int          
    cantidad_utilizada: float

class InsumoServicioCreate(InsumoServicioBase):
    pass  

class InsumoDelServicioResponse(BaseModel):
    cantidad_utilizada: float
    insumo: InsumoServicioDetalle
    class Config: from_attributes = True

class ServicioBase(BaseModel):
    nombre: str
    precio: float = 0.0

    @field_validator("precio")
    @classmethod
    def validar_precio_no_negativo(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError("El precio del servicio no puede ser negativo.")
        return v

class ServicioCreate(ServicioBase):
    id_unidad_limpieza: int
    id_modalidad: int
    insumos_utilizados: List[InsumoServicioCreate] = [] 

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    baja: Optional[bool] = None
    id_unidad_limpieza: Optional[int] = None
    id_modalidad: Optional[int] = None
    insumos_utilizados: Optional[List[InsumoServicioCreate]] = None 

class ServicioResponse(ServicioBase):
    id: int
    baja: bool
    unidad_limpieza: UnidadLimpiezaResponse
    modalidad: ModalidadServicioResponse
    insumos_utilizados: List[InsumoDelServicioResponse] = [] 

    class Config:
        from_attributes = True