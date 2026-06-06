from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import unidades_limpieza as schemas_unidades
from app.services import unidades_limpieza as services_unidades
from app.dependencies.auth import get_current_user, RoleChecker
from app import models

router = APIRouter(
    prefix="/unidades-limpieza",
    tags=["Unidades de Limpieza"]
)

@router.post("/", response_model=schemas_unidades.UnidadLimpiezaResponse, status_code=status.HTTP_201_CREATED)
def crear_unidad(
    unidad: schemas_unidades.UnidadLimpiezaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    return services_unidades.create(db=db, unidad=unidad)

@router.get("/", response_model=List[schemas_unidades.UnidadLimpiezaResponse])
def obtener_unidades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return services_unidades.get_all(db, skip=skip, limit=limit)

@router.get("/{unidad_id}", response_model=schemas_unidades.UnidadLimpiezaResponse)
def obtener_unidad_por_id(
    unidad_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_unidad = services_unidades.get_by_id(db, unidad_id=unidad_id)
    if db_unidad is None:
        raise HTTPException(status_code=404, detail="Unidad de limpieza no encontrada")
    return db_unidad

@router.patch("/{unidad_id}", response_model=schemas_unidades.UnidadLimpiezaResponse)
def actualizar_unidad(
    unidad_id: int,
    unidad: schemas_unidades.UnidadLimpiezaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_unidad = services_unidades.update(db, unidad_id=unidad_id, unidad_data=unidad)
    if db_unidad is None:
        raise HTTPException(status_code=404, detail="Unidad de limpieza no encontrada")
    return db_unidad

@router.delete("/{unidad_id}", response_model=schemas_unidades.UnidadLimpiezaResponse)
def eliminar_unidad(
    unidad_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_unidad = services_unidades.delete(db, unidad_id=unidad_id)
    if db_unidad is None:
        raise HTTPException(status_code=404, detail="Unidad de limpieza no encontrada")
    return db_unidad