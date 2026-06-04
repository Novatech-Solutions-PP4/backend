from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app import models
from app.schemas import servicios as schemas_servicios

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Servicio)\
             .options(
                 joinedload(models.Servicio.unidad_limpieza),
                 joinedload(models.Servicio.modalidad),
                 joinedload(models.Servicio.insumos_utilizados).joinedload(models.InsumosServicios.insumo)
             )\
             .filter(models.Servicio.baja == False)\
             .offset(skip).limit(limit).all()


def get_by_id(db: Session, servicio_id: int):
    db_servicio = db.query(models.Servicio)\
                    .options(
                        joinedload(models.Servicio.unidad_limpieza),
                        joinedload(models.Servicio.modalidad),
                        joinedload(models.Servicio.insumos_utilizados).joinedload(models.InsumosServicios.insumo)
                    )\
                    .filter(models.Servicio.id == servicio_id, models.Servicio.baja == False)\
                    .first()
    
    if not db_servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el servicio con el ID {servicio_id} o ya no está disponible."
        )
    return db_servicio


def create(db: Session, servicio: schemas_servicios.ServicioCreate):
    datos_servicio = servicio.model_dump()
    insumos_data = datos_servicio.pop("insumos_utilizados", [])
    
    if not db.query(models.UnidadLimpieza).filter(models.UnidadLimpieza.id == servicio.id_unidad_limpieza).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear: La unidad de limpieza con ID {servicio.id_unidad_limpieza} no existe."
        )
        
    if not db.query(models.ModalidadServicio).filter(models.ModalidadServicio.id == servicio.id_modalidad).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear: La modalidad de servicio con ID {servicio.id_modalidad} no existe."
        )
        
    for item in insumos_data:
        id_insumo = item["id_insumo"]
        if not db.query(models.Insumo).filter(models.Insumo.id == id_insumo, models.Insumo.baja == False).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear: El insumo con ID {id_insumo} no existe o se encuentra de baja."
            )

    nuevo_servicio = models.Servicio(**datos_servicio)
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    
    for item in insumos_data:
        nuevo_insumo_servicio = models.InsumosServicios(
            id_servicio=nuevo_servicio.id,
            id_insumo=item["id_insumo"],
            cantidad_utilizada=item["cantidad_utilizada"]
        )
        db.add(nuevo_insumo_servicio)
    
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio


def update(db: Session, servicio_id: int, servicio_data: schemas_servicios.ServicioUpdate):
    db_servicio = get_by_id(db, servicio_id)
        
    datos_actualizar = servicio_data.model_dump(exclude_unset=True)
    
    if "id_unidad_limpieza" in datos_actualizar:
        id_un = datos_actualizar["id_unidad_limpieza"]
        if not db.query(models.UnidadLimpieza).filter(models.UnidadLimpieza.id == id_un).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar: La unidad de limpieza con ID {id_un} no existe."
            )

    if "id_modalidad" in datos_actualizar:
        id_mod = datos_actualizar["id_modalidad"]
        if not db.query(models.ModalidadServicio).filter(models.ModalidadServicio.id == id_mod).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar: La modalidad de servicio con ID {id_mod} no existe."
            )

    if "insumos_utilizados" in datos_actualizar:
        insumos_data = datos_actualizar.pop("insumos_utilizados")
        
        for item in insumos_data:
            id_insumo = item["id_insumo"]
            if not db.query(models.Insumo).filter(models.Insumo.id == id_insumo, models.Insumo.baja == False).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al actualizar: El insumo con ID {id_insumo} no existe o está dado de baja."
                )
        
        db.query(models.InsumosServicios).filter(models.InsumosServicios.id_servicio == servicio_id).delete()
        
        for item in insumos_data:
            nuevo_insumo_servicio = models.InsumosServicios(
                id_servicio=servicio_id,
                id_insumo=item["id_insumo"],
                cantidad_utilizada=item["cantidad_utilizada"]
            )
            db.add(nuevo_insumo_servicio)

    for key, value in datos_actualizar.items():
        setattr(db_servicio, key, value)
        
    db.commit()
    db.refresh(db_servicio)
    return db_servicio


def delete(db: Session, servicio_id: int):
    db_servicio = get_by_id(db, servicio_id)
    db_servicio.baja = True
    db.commit()
    db.refresh(db_servicio)
    return db_servicio