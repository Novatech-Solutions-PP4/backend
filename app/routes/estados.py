from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import estados as schemas_estados
from app.services import estados as services_estados

router = APIRouter(
    prefix="/estados",
    tags=["Estados"]
)

@router.get("/", response_model=List[schemas_estados.EstadoResponse])
def obtener_estados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services_estados.get_all(db, skip=skip, limit=limit)

@router.get("/{estado_id}", response_model=schemas_estados.EstadoResponse)
def obtener_estado_por_id(estado_id: int, db: Session = Depends(get_db)):
    db_estado = services_estados.get_by_id(db, estado_id=estado_id)
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return db_estado