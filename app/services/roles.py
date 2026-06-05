from sqlalchemy.orm import Session
from app import models
from app.schemas import roles as schemas_roles
from fastapi import HTTPException, status

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Rol).offset(skip).limit(limit).all()

def get_by_id(db: Session, rol_id: int):
    db_rol = db.query(models.Rol).filter(models.Rol.id == rol_id).first()
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el Rol con el ID {rol_id}."
        )
    return db_rol

def get_by_nombre(db: Session, nombre: str):
    return db.query(models.Rol).filter(models.Rol.nombre == nombre).first()