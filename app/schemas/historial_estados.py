from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.estados import EstadoResponse

class UsuarioMinResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    email: str
    telefono: Optional[str] = None

    class Config:
        from_attributes = True

class HistorialEstadosBase(BaseModel):
    id_usuario: int
    id_pedido: int
    id_estado: int
    fecha_hora: datetime

class HistorialEstadosCreate(HistorialEstadosBase):
    pass

class HistorialEstadosResponse(HistorialEstadosBase):
    id: int
    usuario: UsuarioMinResponse
    estado: EstadoResponse

    class Config:
        from_attributes = True