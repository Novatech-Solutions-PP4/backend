from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from typing import List, Optional
from app import models
from app.schemas import pedidos as schemas_pedidos
from app.services import mercadopago

def get_all(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None, is_client: bool = False):
    
    query = db.query(models.Pedido).options(
        joinedload(models.Pedido.usuario),
        joinedload(models.Pedido.detalles).joinedload(models.DetalleServicio.servicio).joinedload(models.Servicio.unidad_limpieza),
        joinedload(models.Pedido.detalles).joinedload(models.DetalleServicio.servicio).joinedload(models.Servicio.modalidad),
        joinedload(models.Pedido.pagos).joinedload(models.FacturacionPagos.metodo_pago),
        joinedload(models.Pedido.historial_estados).joinedload(models.HistorialEstados.estado),
        joinedload(models.Pedido.historial_estados).joinedload(models.HistorialEstados.usuario)
    ).filter(models.Pedido.baja == False)
    
    if is_client and user_id:
        query = query.filter(models.Pedido.id_usuario == user_id)
        
    return query.order_by(models.Pedido.fecha_recepcion.desc()).offset(skip).limit(limit).all()

def get_by_id(db: Session, pedido_id: int, user_id: Optional[int] = None, is_client: bool = False):
    
    query = db.query(models.Pedido).options(
        joinedload(models.Pedido.usuario),
        joinedload(models.Pedido.detalles).joinedload(models.DetalleServicio.servicio).joinedload(models.Servicio.unidad_limpieza),
        joinedload(models.Pedido.detalles).joinedload(models.DetalleServicio.servicio).joinedload(models.Servicio.modalidad),
        joinedload(models.Pedido.pagos).joinedload(models.FacturacionPagos.metodo_pago),
        joinedload(models.Pedido.historial_estados).joinedload(models.HistorialEstados.estado),
        joinedload(models.Pedido.historial_estados).joinedload(models.HistorialEstados.usuario)
    ).filter(models.Pedido.id == pedido_id, models.Pedido.baja == False)
    
    if is_client and user_id:
        query = query.filter(models.Pedido.id_usuario == user_id)
        
    pedido = query.first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID {pedido_id} no encontrado."
        )
    return pedido

def create(db: Session, pedido: schemas_pedidos.PedidoCreate, id_metodo_pago: int, creador_id: int):
    
    
    cliente = db.query(models.Usuario).filter(models.Usuario.id == pedido.id_usuario, models.Usuario.baja == False).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con ID {pedido.id_usuario} no existe."
        )
        
    
    metodo_pago = db.query(models.MetodoPago).filter(models.MetodoPago.id == id_metodo_pago).first()
    if not metodo_pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El método de pago con ID {id_metodo_pago} no existe."
        )
        
    
    servicios_db = []
    monto_total = 0.0
    for id_serv in pedido.id_servicios:
        serv = db.query(models.Servicio).filter(models.Servicio.id == id_serv, models.Servicio.baja == False).first()
        if not serv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El servicio con ID {id_serv} no existe o fue dado de baja."
            )
        servicios_db.append(serv)
        monto_total += serv.precio
        
    
    nuevo_pedido = models.Pedido(
        id_usuario=pedido.id_usuario,
        estado_actual="Pendiente",
        fecha_recepcion=datetime.now(timezone.utc),
        fecha_entrega_estimada=None,
        monto_actual=monto_total,
        baja=False
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    
    
    nuevo_pedido.codigo_qr = f"LAVAPRO-PED-{nuevo_pedido.id}"
    db.commit()
    
    
    for serv in servicios_db:
        detalle = models.DetalleServicio(
            id_pedido=nuevo_pedido.id,
            id_servicio=serv.id,
            precio_unitario_momento=serv.precio
        )
        db.add(detalle)
        
        
        for insumo_utilizado in serv.insumos_utilizados:
            insumo_db = db.query(models.Insumo).filter(
                models.Insumo.id == insumo_utilizado.id_insumo,
                models.Insumo.baja == False
            ).first()
            if insumo_db:
                insumo_db.cantidad -= insumo_utilizado.cantidad_utilizada
        
    
    estado_pendiente = db.query(models.Estado).filter(models.Estado.nombre.ilike("pendiente")).first()
    id_est = estado_pendiente.id if estado_pendiente else 1
    
    historial = models.HistorialEstados(
        id_usuario=creador_id, 
        id_pedido=nuevo_pedido.id,
        id_estado=id_est,
        fecha_hora=datetime.now(timezone.utc)
    )
    db.add(historial)
    
    
    nuevo_pago = models.FacturacionPagos(
        id_pedido=nuevo_pedido.id,
        id_metodo_pago=metodo_pago.id,
        estado="pending",
        monto=monto_total,
        fecha_pago=None
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    
    
    init_point = None
    if metodo_pago.nombre.lower() == "mercado pago":
        pref = mercadopago.crear_preferencia_pago(
            pedido_id=nuevo_pedido.id,
            monto=monto_total,
            email_cliente=cliente.email
        )
        nuevo_pago.id_transaccion_externa = pref["preference_id"]
        db.commit()
        init_point = pref["init_point"]
        
    
    pedido_completo = get_by_id(db, nuevo_pedido.id)
    
    return {
        "pedido": pedido_completo,
        "init_point_mercadopago": init_point
    }

def update(db: Session, pedido_id: int, pedido_data: schemas_pedidos.PedidoUpdate, usuario_operador_id: int):
    
    db_pedido = get_by_id(db, pedido_id)
    
    datos_actualizar = pedido_data.model_dump(exclude_unset=True)
    
    
    if "status" in datos_actualizar:
        datos_actualizar["estado_actual"] = datos_actualizar.pop("status")
        
    
    if "total" in datos_actualizar:
        datos_actualizar["monto_actual"] = datos_actualizar.pop("total")
    
    if "estado_actual" in datos_actualizar:
        nuevo_estado_nombre = datos_actualizar["estado_actual"]
        
        
        estado_db = db.query(models.Estado).filter(models.Estado.nombre.ilike(nuevo_estado_nombre)).first()
        if not estado_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estado '{nuevo_estado_nombre}' no es un estado válido de trazabilidad."
            )
            
        
        if db_pedido.estado_actual != nuevo_estado_nombre:
            historial = models.HistorialEstados(
                id_usuario=usuario_operador_id,
                id_pedido=db_pedido.id,
                id_estado=estado_db.id,
                fecha_hora=datetime.now(timezone.utc)
            )
            db.add(historial)
            
    
    if "monto_actual" in datos_actualizar:
        nuevo_monto = datos_actualizar["monto_actual"]
        pago_db = db.query(models.FacturacionPagos).filter(
            models.FacturacionPagos.id_pedido == db_pedido.id
        ).first()
        if pago_db:
            pago_db.monto = nuevo_monto
            
    for key, value in datos_actualizar.items():
        if hasattr(db_pedido, key):
            setattr(db_pedido, key, value)
        
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def delete(db: Session, pedido_id: int):
    
    db_pedido = get_by_id(db, pedido_id)
    db_pedido.baja = True
    db.commit()
    db.refresh(db_pedido)
    return db_pedido
