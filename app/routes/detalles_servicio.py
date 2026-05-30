from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import detalles_servicio as schemas_detalles_servicio
from app.services import detalles_servicio as services_detalles_servicio

router = APIRouter(
    prefix="/detalles-servicio",
    tags=["DetallesServicio"]
)

@router.post("/", response_model=schemas_detalles_servicio.DetalleServicioResponse)
def crear_detalle_servicio(item: schemas_detalles_servicio.DetalleServicioCreate, db: Session = Depends(get_db)):
    return services_detalles_servicio.create(db=db, item=item)

@router.get("/", response_model=List[schemas_detalles_servicio.DetalleServicioResponse])
def obtener_detalles_servicio(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services_detalles_servicio.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=schemas_detalles_servicio.DetalleServicioResponse)
def obtener_detalle_servicio_por_id(id: int, db: Session = Depends(get_db)):
    db_item = services_detalles_servicio.get_by_id(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="DetalleServicio no encontrado")
    return db_item

@router.patch("/{id}", response_model=schemas_detalles_servicio.DetalleServicioResponse)
def actualizar_detalle_servicio(id: int, item: schemas_detalles_servicio.DetalleServicioUpdate, db: Session = Depends(get_db)):
    db_item = services_detalles_servicio.update(db, id=id, item_data=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="DetalleServicio no encontrado")
    return db_item

@router.delete("/{id}", response_model=schemas_detalles_servicio.DetalleServicioResponse)
def eliminar_detalle_servicio(id: int, db: Session = Depends(get_db)):
    db_item = services_detalles_servicio.delete(db, id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="DetalleServicio no encontrado")
    return db_item
