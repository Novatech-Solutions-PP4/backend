from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from typing import List, Optional
from app import models
from app.schemas import reclamos as schemas_reclamos

def get_all(db: Session, skip: int = 0, limit: int = 100, user_role: Optional[str] = None, client_name: Optional[str] = None):
    
    query = db.query(models.Reclamo).options(
        joinedload(models.Reclamo.estado_rel),
        joinedload(models.Reclamo.categoria_rel),
        joinedload(models.Reclamo.pedido).joinedload(models.Pedido.usuario),
        joinedload(models.Reclamo.mensajes).joinedload(models.MensajeReclamo.usuario).joinedload(models.Usuario.rol)
    )
    
    if user_role == "cliente" and client_name:
        query = query.join(models.Pedido).join(models.Usuario).filter(models.Usuario.nombre.ilike(client_name))
        
    return query.order_by(models.Reclamo.fecha_creacion.desc()).offset(skip).limit(limit).all()

def get_by_id(db: Session, reclamo_id: int):
    
    reclamo = db.query(models.Reclamo).options(
        joinedload(models.Reclamo.estado_rel),
        joinedload(models.Reclamo.categoria_rel),
        joinedload(models.Reclamo.pedido).joinedload(models.Pedido.usuario),
        joinedload(models.Reclamo.mensajes).joinedload(models.MensajeReclamo.usuario).joinedload(models.Usuario.rol)
    ).filter(models.Reclamo.id == reclamo_id).first()
    
    if not reclamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reclamo con ID {reclamo_id} no encontrado."
        )
    return reclamo

def create(db: Session, reclamo: schemas_reclamos.ReclamoCreate, creator_id: int):
    
    
    pedido = db.query(models.Pedido).filter(models.Pedido.id == reclamo.id_pedido, models.Pedido.baja == False).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {reclamo.id_pedido} no existe."
        )
        
    
    categoria = db.query(models.CategoriaReclamo).filter(models.CategoriaReclamo.id == reclamo.id_categoria).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría de reclamo con ID {reclamo.id_categoria} no existe."
        )
        
    
    estado = db.query(models.EstadoReclamo).filter(models.EstadoReclamo.nombre.ilike("En Revisión")).first()
    if not estado:
        
        estado = db.query(models.EstadoReclamo).first()
        
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No hay estados de reclamo cargados en el sistema."
        )
        
    
    nuevo_reclamo = models.Reclamo(
        id_pedido=reclamo.id_pedido,
        id_categoria=reclamo.id_categoria,
        id_estado=estado.id,
        fecha_creacion=datetime.now(timezone.utc)
    )
    db.add(nuevo_reclamo)
    db.commit()
    db.refresh(nuevo_reclamo)
    
    
    if reclamo.mensaje_inicial:
        nuevo_mensaje = models.MensajeReclamo(
            id_reclamo=nuevo_reclamo.id,
            id_usuario=creator_id,
            mensaje=reclamo.mensaje_inicial,
            fecha_envio=datetime.now(timezone.utc)
        )
        db.add(nuevo_mensaje)
        db.commit()
        
    return get_by_id(db, nuevo_reclamo.id)

def update(db: Session, reclamo_id: int, reclamo_update: schemas_reclamos.ReclamoUpdate):
    
    db_reclamo = get_by_id(db, reclamo_id)
    
    datos_actualizar = reclamo_update.model_dump(exclude_unset=True)
    
    
    if "status" in datos_actualizar:
        status_nombre = datos_actualizar.pop("status")
        estado_db = db.query(models.EstadoReclamo).filter(models.EstadoReclamo.nombre.ilike(status_nombre)).first()
        if not estado_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estado '{status_nombre}' no es válido para reclamos."
            )
        db_reclamo.id_estado = estado_db.id
        
    if "id_estado" in datos_actualizar:
        id_est = datos_actualizar["id_estado"]
        estado_db = db.query(models.EstadoReclamo).filter(models.EstadoReclamo.id == id_est).first()
        if not estado_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estado con ID {id_est} no existe."
            )
        db_reclamo.id_estado = id_est
        
    db.commit()
    db.refresh(db_reclamo)
    return db_reclamo

def create_message(db: Session, reclamo_id: int, mensaje: schemas_reclamos.MensajeReclamoCreate, usuario_id: int):
    
    
    db_reclamo = get_by_id(db, reclamo_id)
    
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id, models.Usuario.baja == False).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con ID {usuario_id} no existe o fue dado de baja."
        )
        
    
    nuevo_mensaje = models.MensajeReclamo(
        id_reclamo=reclamo_id,
        id_usuario=usuario_id,
        mensaje=mensaje.mensaje,
        fecha_envio=datetime.now(timezone.utc)
    )
    db.add(nuevo_mensaje)
    db.commit()
    db.refresh(nuevo_mensaje)
    
    
    return db.query(models.MensajeReclamo).options(
        joinedload(models.MensajeReclamo.usuario).joinedload(models.Usuario.rol)
    ).filter(models.MensajeReclamo.id == nuevo_mensaje.id).first()

def mark_messages_as_read(db: Session, reclamo_id: int, current_user_id: int):
    
    db.query(models.MensajeReclamo).filter(
        models.MensajeReclamo.id_reclamo == reclamo_id,
        models.MensajeReclamo.id_usuario != current_user_id,
        models.MensajeReclamo.leido == False
    ).update({models.MensajeReclamo.leido: True}, synchronize_session=False)
    db.commit()

