from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import servicios as schemas_servicios
from app.services import servicios as services_servicios
from app.dependencies.auth import get_current_user, RoleChecker
from app import models

router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"]
)

@router.post("/", response_model=schemas_servicios.ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(
    servicio: schemas_servicios.ServicioCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    return services_servicios.create(db=db, servicio=servicio)

@router.get("/", response_model=List[schemas_servicios.ServicioResponse])
def obtener_servicios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return services_servicios.get_all(db, skip=skip, limit=limit)

@router.get("/{servicio_id}", response_model=schemas_servicios.ServicioResponse)
def obtener_servicio_por_id(
    servicio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_servicio = services_servicios.get_by_id(db, servicio_id=servicio_id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

@router.patch("/{servicio_id}", response_model=schemas_servicios.ServicioResponse)
def actualizar_servicio(
    servicio_id: int, 
    servicio: schemas_servicios.ServicioUpdate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_servicio = services_servicios.update(db, servicio_id=servicio_id, servicio_data=servicio)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

@router.delete("/{servicio_id}", response_model=schemas_servicios.ServicioResponse)
def eliminar_servicio(
    servicio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_servicio = services_servicios.delete(db, servicio_id=servicio_id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio