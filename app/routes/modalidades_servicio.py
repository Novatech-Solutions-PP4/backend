from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import modalidades_servicio as schemas_modalidades_servicio
from app.services import modalidades_servicio as services_modalidades_servicio

router = APIRouter(
    prefix="/modalidades-servicio",
    tags=["ModalidadesServicio"]
)

@router.post("/", response_model=schemas_modalidades_servicio.ModalidadServicioResponse)
def crear_modalidad_servicio(item: schemas_modalidades_servicio.ModalidadServicioCreate, db: Session = Depends(get_db)):
    return services_modalidades_servicio.create(db=db, item=item)

@router.get("/", response_model=List[schemas_modalidades_servicio.ModalidadServicioResponse])
def obtener_modalidades_servicio(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services_modalidades_servicio.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=schemas_modalidades_servicio.ModalidadServicioResponse)
def obtener_modalidad_servicio_por_id(id: int, db: Session = Depends(get_db)):
    db_item = services_modalidades_servicio.get_by_id(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="ModalidadServicio no encontrada")
    return db_item

@router.patch("/{id}", response_model=schemas_modalidades_servicio.ModalidadServicioResponse)
def actualizar_modalidad_servicio(id: int, item: schemas_modalidades_servicio.ModalidadServicioUpdate, db: Session = Depends(get_db)):
    db_item = services_modalidades_servicio.update(db, id=id, item_data=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="ModalidadServicio no encontrada")
    return db_item

@router.delete("/{id}", response_model=schemas_modalidades_servicio.ModalidadServicioResponse)
def eliminar_modalidad_servicio(id: int, db: Session = Depends(get_db)):
    db_item = services_modalidades_servicio.delete(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="ModalidadServicio no encontrada")
    return db_item
