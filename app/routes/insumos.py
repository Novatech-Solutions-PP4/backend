from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import insumos as schemas_insumos
from app.services import insumos as services_insumos
from app.dependencies.auth import RoleChecker
from app import models

router = APIRouter(
    prefix="/insumos",
    tags=["Insumos"]
)

@router.post("/", response_model=schemas_insumos.InsumoResponse, status_code=status.HTTP_201_CREATED)
def crear_insumo(
    insumo: schemas_insumos.InsumoCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    return services_insumos.create(db=db, insumo=insumo)

@router.get("/", response_model=List[schemas_insumos.InsumoResponse])
def obtener_insumos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    return services_insumos.get_all(db, skip=skip, limit=limit)

@router.get("/{insumo_id}", response_model=schemas_insumos.InsumoResponse)
def obtener_insumo_por_id(
    insumo_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    db_insumo = services_insumos.get_by_id(db, insumo_id=insumo_id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo

@router.patch("/{insumo_id}", response_model=schemas_insumos.InsumoResponse)
def actualizar_insumo(
    insumo_id: int, 
    insumo: schemas_insumos.InsumoUpdate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_insumo = services_insumos.update(db, insumo_id=insumo_id, insumo_data=insumo)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo

@router.delete("/{insumo_id}", response_model=schemas_insumos.InsumoResponse)
def eliminar_insumo(
    insumo_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_insumo = services_insumos.delete(db, insumo_id=insumo_id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo