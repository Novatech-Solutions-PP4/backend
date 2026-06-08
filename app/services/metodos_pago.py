from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import models

def get_all(db: Session):
    
    return db.query(models.MetodoPago).all()

def get_by_id(db: Session, metodo_id: int):
    
    metodo = db.query(models.MetodoPago).filter(models.MetodoPago.id == metodo_id).first()
    if not metodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Método de pago con ID {metodo_id} no encontrado."
        )
    return metodo

def get_by_name(db: Session, nombre: str):
    
    metodo = db.query(models.MetodoPago).filter(models.MetodoPago.nombre.ilike(nombre)).first()
    if not metodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Método de pago con el nombre '{nombre}' no encontrado."
        )
    return metodo
