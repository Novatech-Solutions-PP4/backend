from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime





class MensajeReclamoCreate(BaseModel):
    mensaje: str = Field(..., description="Contenido de texto del mensaje")

class MensajeReclamoResponse(BaseModel):
    id: int
    id_reclamo: int
    id_usuario: int
    mensaje: str
    fecha_envio: datetime
    leido: bool
    
    
    sender: str
    text: str
    time: str
    senderName: str

    class Config:
        from_attributes = True





class ReclamoCreate(BaseModel):
    id_pedido: int = Field(..., description="ID del pedido asociado al reclamo")
    id_categoria: int = Field(..., description="ID de la categoría del reclamo (motivo)")
    mensaje_inicial: Optional[str] = Field(None, description="Mensaje explicativo inicial para abrir el reclamo")

class ReclamoUpdate(BaseModel):
    id_estado: Optional[int] = Field(None, description="ID del nuevo estado del reclamo")
    status: Optional[str] = Field(None, description="Nombre del nuevo estado (Abierto, En Revisión, Resuelto) para compatibilidad")

class ReclamoResponse(BaseModel):
    id: int
    id_pedido: int
    id_categoria: int
    id_estado: int
    fecha_creacion: datetime
    
    
    pedidoId: str
    cliente: str
    status: str
    categoria: str
    fecha: str
    
    mensajes: List[MensajeReclamoResponse] = []
    unread_count: int = 0

    class Config:
        from_attributes = True
