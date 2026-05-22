from sqlalchemy.orm import Session
from app import models
from app.schemas import insumos as schemas_insumos

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Insumo).filter(models.Insumo.baja == False).offset(skip).limit(limit).all()

def get_by_id(db: Session, insumo_id: int):
    return db.query(models.Insumo).filter(models.Insumo.id == insumo_id, models.Insumo.baja == False).first()

def create(db: Session, insumo: schemas_insumos.InsumoCreate):
    nuevo_insumo = models.Insumo(**insumo.model_dump())
    db.add(nuevo_insumo)
    db.commit()
    db.refresh(nuevo_insumo)
    return nuevo_insumo

def update(db: Session, insumo_id: int, insumo_data: schemas_insumos.InsumoUpdate):
    db_insumo = get_by_id(db, insumo_id)
    if not db_insumo:
        return None
    datos_actualizar = insumo_data.model_dump(exclude_unset=True)
    for key, value in datos_actualizar.items():
        setattr(db_insumo, key, value) 
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

def delete(db: Session, insumo_id: int):
    db_insumo = get_by_id(db, insumo_id)
    if not db_insumo:
        return None
    db_insumo.baja = True
    db.commit()
    db.refresh(db_insumo)
    return db_insumo