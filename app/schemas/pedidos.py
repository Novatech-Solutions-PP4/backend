from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


from app.schemas.unidades_limpieza import UnidadLimpiezaResponse
from app.schemas.modalidades_servicio import ModalidadServicioResponse
from app.schemas.historial_estados import HistorialEstadosResponse





class PedidoCreate(BaseModel):
    
    id_usuario: int = Field(..., description="ID del cliente dueño de la ropa")
    id_servicios: List[int] = Field(..., min_length=1, description="Lista de IDs de servicios asociados al pedido")


class PedidoUpdate(BaseModel):
    
    estado_actual: Optional[str] = Field(None, description="Ej: 'En Proceso', 'Listo', 'Entregado'")
    status: Optional[str] = Field(None, description="Equivalente a estado_actual para compatibilidad con el frontend")
    fecha_entrega_estimada: Optional[datetime] = None
    baja: Optional[bool] = None
    monto_actual: Optional[float] = None
    total: Optional[float] = Field(None, description="Equivalente a monto_actual para compatibilidad con el frontend (solo administradores)")






class UsuarioMinResponse(BaseModel):
    
    id: int
    nombre: str
    apellido: str
    dni: str
    email: str
    telefono: Optional[str] = None

    class Config:
        from_attributes = True


class MetodoPagoMinResponse(BaseModel):
    
    id: int
    nombre: str

    class Config:
        from_attributes = True


class FacturacionPagosResponse(BaseModel):
    
    id: int
    id_transaccion_externa: Optional[str] = None
    estado: str  
    monto: float
    fecha_pago: Optional[datetime] = None
    metodo_pago: MetodoPagoMinResponse  

    class Config:
        from_attributes = True


class ServicioPedidoResponse(BaseModel):
    
    id: int
    nombre: str
    unidad_limpieza: UnidadLimpiezaResponse
    modalidad: ModalidadServicioResponse

    class Config:
        from_attributes = True


class DetalleServicioResponse(BaseModel):
    
    id: int
    precio_unitario_momento: float
    servicio: ServicioPedidoResponse  

    class Config:
        from_attributes = True






class PedidoResponse(BaseModel):
    
    id: int
    codigo_qr: Optional[str] = None
    estado_actual: str  
    fecha_recepcion: datetime
    fecha_entrega_estimada: Optional[datetime] = None
    monto_actual: float
    baja: bool
    
    usuario: UsuarioMinResponse  
    detalles: List[DetalleServicioResponse] = []  
    pagos: List[FacturacionPagosResponse] = []  
    historial_estados: List[HistorialEstadosResponse] = []  

    class Config:
        from_attributes = True


class PedidoCreadoConPagoResponse(BaseModel):
    
    pedido: PedidoResponse
    init_point_mercadopago: Optional[str] = Field(None, description="URL generada por Mercado Pago para cobrar")