from sqlalchemy.orm import Session
from app import models
from app.schemas import servicios as schemas_servicios

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Servicio).filter(models.Servicio.baja == False).offset(skip).limit(limit).all()

def get_by_id(db: Session, servicio_id: int):
    return db.query(models.Servicio).filter(models.Servicio.id == servicio_id, models.Servicio.baja == False).first()

def create(db: Session, servicio: schemas_servicios.ServicioCreate):
    nuevo_servicio = models.Servicio(**servicio.model_dump())
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio

def update(db: Session, servicio_id: int, servicio_data: schemas_servicios.ServicioUpdate):
    db_servicio = get_by_id(db, servicio_id)
    if not db_servicio:
        return None
    datos_actualizar = servicio_data.model_dump(exclude_unset=True)
    for key, value in datos_actualizar.items():
        setattr(db_servicio, key, value) 
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

def delete(db: Session, servicio_id: int):
    db_servicio = get_by_id(db, servicio_id)
    if not db_servicio:
        return None
    db_servicio.baja = True
    db.commit()
    db.refresh(db_servicio)
    return db_servicio