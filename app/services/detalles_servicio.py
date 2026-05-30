from sqlalchemy.orm import Session
from app import models
from app.schemas import detalles_servicio as schemas_detalles_servicio

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DetalleServicio).offset(skip).limit(limit).all()

def get_by_id(db: Session, id: int):
    return db.query(models.DetalleServicio).filter(models.DetalleServicio.id == id).first()

def create(db: Session, item: schemas_detalles_servicio.DetalleServicioCreate):
    nuevo_item = models.DetalleServicio(**item.model_dump())
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    return nuevo_item

def update(db: Session, id: int, item_data: schemas_detalles_servicio.DetalleServicioUpdate):
    db_item = get_by_id(db, id)
    if not db_item:
        return None
    datos_actualizar = item_data.model_dump(exclude_unset=True)
    for key, value in datos_actualizar.items():
        setattr(db_item, key, value) 
    db.commit()
    db.refresh(db_item)
    return db_item

def delete(db: Session, id: int):
    db_item = get_by_id(db, id)
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
