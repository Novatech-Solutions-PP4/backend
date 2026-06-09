from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import metodos_pago as schemas_metodos
from app.services import metodos_pago as services_metodos
from app.dependencies.auth import get_current_user
from app import models

router = APIRouter(
    prefix="/metodos-pago",
    tags=["Métodos de Pago"]
)

@router.get("/", response_model=List[schemas_metodos.MetodoPagoResponse])
def obtener_metodos_pago(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    
    return services_metodos.get_all(db)

@router.get("/{metodo_id}", response_model=schemas_metodos.MetodoPagoResponse)
def obtener_metodo_pago_por_id(
    metodo_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    
    return services_metodos.get_by_id(db, metodo_id=metodo_id)

@router.get("/nombre/{nombre}", response_model=schemas_metodos.MetodoPagoResponse)
def obtener_metodo_pago_por_nombre(
    nombre: str, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    
    return services_metodos.get_by_name(db, nombre=nombre)
