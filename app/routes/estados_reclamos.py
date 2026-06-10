from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import estados_reclamos as schemas_estados
from app.services import estados_reclamos as services_estados
from app.dependencies.auth import get_current_user
from app import models

router = APIRouter(
    prefix="/reclamos/estados",
    tags=["Estados de Reclamos"]
)

@router.get("", response_model=List[schemas_estados.EstadoReclamoResponse])
def obtener_estados_reclamos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return services_estados.get_all(db, skip=skip, limit=limit)

@router.get("/{estado_id}", response_model=schemas_estados.EstadoReclamoResponse)
def obtener_estado_reclamo_por_id(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_estado = services_estados.get_by_id(db, estado_id=estado_id)
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado de reclamo no encontrado")
    return db_estado