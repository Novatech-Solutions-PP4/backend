from sqlalchemy.orm import Session
from app import models

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Estado).offset(skip).limit(limit).all()

def get_by_id(db: Session, estado_id: int):
    return db.query(models.Estado).filter(models.Estado.id == estado_id).first()
