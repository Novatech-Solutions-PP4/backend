from sqlalchemy.orm import Session
from app import models
from app.schemas import estados_reclamos as schemas_estados

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.EstadoReclamo).offset(skip).limit(limit).all()

def get_by_id(db: Session, estado_id: int):
    return db.query(models.EstadoReclamo).filter(models.EstadoReclamo.id == estado_id).first()

def get_by_nombre(db: Session, nombre: str):
    return db.query(models.EstadoReclamo).filter(models.EstadoReclamo.nombre.ilike(nombre)).first()
