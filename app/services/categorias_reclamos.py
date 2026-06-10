from sqlalchemy.orm import Session
from app import models
from app.schemas import categorias_reclamos as schemas_categorias

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CategoriaReclamo).offset(skip).limit(limit).all()

def get_by_id(db: Session, categoria_id: int):
    return db.query(models.CategoriaReclamo).filter(models.CategoriaReclamo.id == categoria_id).first()

def get_by_nombre(db: Session, nombre: str):
    return db.query(models.CategoriaReclamo).filter(models.CategoriaReclamo.nombre.ilike(nombre)).first()
