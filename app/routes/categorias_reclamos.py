from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import categorias_reclamos as schemas_categorias
from app.services import categorias_reclamos as services_categorias
from app.dependencies.auth import get_current_user
from app import models

router = APIRouter(
    prefix="/reclamos/categorias",
    tags=["Categorías de Reclamos"]
)

@router.get("", response_model=List[schemas_categorias.CategoriaReclamoResponse])
def obtener_categorias_reclamos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return services_categorias.get_all(db, skip=skip, limit=limit)

@router.get("/{categoria_id}", response_model=schemas_categorias.CategoriaReclamoResponse)
def obtener_categoria_reclamo_por_id(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_categoria = services_categorias.get_by_id(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría de reclamo no encontrada")
    return db_categoria