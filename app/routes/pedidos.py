from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app import models
from app.schemas import pedidos as schemas_pedidos
from app.schemas import metodos_pago as schemas_metodos_pago
from app.services import pedidos as services_pedidos
from app.services import metodos_pago as services_metodos_pago
from app.services import mercadopago
from app.dependencies.auth import get_current_user, RoleChecker

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)





@router.post("/", response_model=schemas_pedidos.PedidoCreadoConPagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido: schemas_pedidos.PedidoCreate,
    id_metodo_pago: int = Query(1, description="ID del método de pago elegido (por defecto 1 = Mercado Pago)"),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"])),
    db: Session = Depends(get_db)
):
    
    return services_pedidos.create(db=db, pedido=pedido, id_metodo_pago=id_metodo_pago, creador_id=current_user.id)


@router.get("/", response_model=List[schemas_pedidos.PedidoResponse])
def obtener_pedidos(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    is_client = current_user.rol.nombre.lower() == "cliente"
    user_id = current_user.id if is_client else None
    return services_pedidos.get_all(db, skip=skip, limit=limit, user_id=user_id, is_client=is_client)


@router.get("/metodos-pago", response_model=List[schemas_metodos_pago.MetodoPagoResponse])
def obtener_metodos_pago(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    return services_metodos_pago.get_all(db)


@router.get("/{pedido_id}", response_model=schemas_pedidos.PedidoResponse)
def obtener_pedido_por_id(
    pedido_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    is_client = current_user.rol.nombre.lower() == "cliente"
    user_id = current_user.id if is_client else None
    return services_pedidos.get_by_id(db, pedido_id=pedido_id, user_id=user_id, is_client=is_client)


@router.patch("/{pedido_id}", response_model=schemas_pedidos.PedidoResponse)
def actualizar_pedido(
    pedido_id: int,
    pedido: schemas_pedidos.PedidoUpdate,
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"])),
    db: Session = Depends(get_db)
):
    
    return services_pedidos.update(db, pedido_id=pedido_id, pedido_data=pedido, usuario_operador_id=current_user.id)


@router.delete("/{pedido_id}", response_model=schemas_pedidos.PedidoResponse)
def eliminar_pedido(
    pedido_id: int,
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"])),
    db: Session = Depends(get_db)
):
    
    return services_pedidos.delete(db, pedido_id=pedido_id)






@router.post("/webhook/mercadopago", status_code=status.HTTP_200_OK)
def webhook_mercadopago(
    payload: dict,
    topic: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    
    payment_id = None
    notification_type = payload.get("type") or topic
    
    if notification_type == "payment":
        payment_id = payload.get("data", {}).get("id") or payload.get("id")
        
    if not payment_id:
        return {"status": "ignored", "message": "Notificación no relacionada a cobros directos."}
        
    info_pago = mercadopago.obtener_estado_pago(str(payment_id))
    
    pedido_id_str = info_pago.get("external_reference")
    if not pedido_id_str or pedido_id_str == "0":
        return {"status": "ignored", "message": "Falta referencia externa (pedido_id)."}
        
    pedido_id = int(pedido_id_str)
    estado_pago = info_pago.get("estado")
    
    pago_db = db.query(models.FacturacionPagos).filter(
        models.FacturacionPagos.id_pedido == pedido_id
    ).first()
    
    if pago_db:
        pago_db.estado = estado_pago
        
        if estado_pago == "approved":
            pago_db.id_transaccion_externa = str(payment_id)
            pago_db.fecha_pago = datetime.now(timezone.utc)
            
        db.commit()
        return {"status": "processed", "payment_id": payment_id, "new_status": estado_pago}
        
    return {"status": "error", "message": f"No se encontró facturación asociada al pedido #{pedido_id}"}


@router.post("/{pedido_id}/simular-pago", status_code=status.HTTP_200_OK)
def simular_pago_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    
    pago = db.query(models.FacturacionPagos).filter(
        models.FacturacionPagos.id_pedido == pedido_id
    ).first()
    
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facturación no encontrada para el pedido #{pedido_id}"
        )
        
    pago.estado = "approved"
    pago.fecha_pago = datetime.now(timezone.utc)
    pago.id_transaccion_externa = f"simulated_{int(datetime.now(timezone.utc).timestamp())}"
    
    db.commit()
    return {"status": "approved", "message": "Pago aprobado simulado con éxito"}

