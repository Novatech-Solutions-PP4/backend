from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app import models

def get_all(db: Session, skip: int = 0, limit: int = 100):
    
    return db.query(models.HistorialEstados).options(
        joinedload(models.HistorialEstados.usuario),
        joinedload(models.HistorialEstados.estado)
    ).offset(skip).limit(limit).all()

def get_by_id(db: Session, history_id: int):
    
    historial = db.query(models.HistorialEstados).options(
        joinedload(models.HistorialEstados.usuario),
        joinedload(models.HistorialEstados.estado)
    ).filter(models.HistorialEstados.id == history_id).first()
    
    if not historial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historial de estado con ID {history_id} no encontrado."
        )
    return historial

def get_by_pedido_id(db: Session, pedido_id: int):
    
    
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id, models.Pedido.baja == False).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID {pedido_id} no existe o fue dado de baja."
        )
        
    return db.query(models.HistorialEstados).options(
        joinedload(models.HistorialEstados.usuario),
        joinedload(models.HistorialEstados.estado)
    ).filter(models.HistorialEstados.id_pedido == pedido_id)\
     .order_by(models.HistorialEstados.fecha_hora.asc()).all()
