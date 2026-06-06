from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import roles as schemas_roles
from app.services import roles as services_roles
from app.dependencies.auth import RoleChecker
from app import models

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.get("/", response_model=List[schemas_roles.RolResponse])
def obtener_roles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    return services_roles.get_all(db, skip=skip, limit=limit)

@router.get("/{rol_id}", response_model=schemas_roles.RolResponse)
def obtener_rol_por_id(
    rol_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    db_rol = services_roles.get_by_id(db, rol_id=rol_id)
    if db_rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return db_rol