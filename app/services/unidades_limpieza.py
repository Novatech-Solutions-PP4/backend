from sqlalchemy.orm import Session
from app import models
from app.schemas import unidades_limpieza as schemas_unidades

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UnidadLimpieza).offset(skip).limit(limit).all()

def get_by_id(db: Session, unidad_id: int):
    return db.query(models.UnidadLimpieza).filter(models.UnidadLimpieza.id == unidad_id).first()

def create(db: Session, unidad: schemas_unidades.UnidadLimpiezaCreate):
    nueva_unidad = models.UnidadLimpieza(**unidad.model_dump())
    db.add(nueva_unidad)
    db.commit()
    db.refresh(nueva_unidad)
    return nueva_unidad

def update(db: Session, unidad_id: int, unidad_data: schemas_unidades.UnidadLimpiezaUpdate):
    db_unidad = get_by_id(db, unidad_id)
    if not db_unidad:
        return None
    datos_actualizar = unidad_data.model_dump(exclude_unset=True)
    for key, value in datos_actualizar.items():
        setattr(db_unidad, key, value)
    db.commit()
    db.refresh(db_unidad)
    return db_unidad

def delete(db: Session, unidad_id: int):
    db_unidad = get_by_id(db, unidad_id)
    if not db_unidad:
        return None
    db.delete(db_unidad)
    db.commit()
    return db_unidad
