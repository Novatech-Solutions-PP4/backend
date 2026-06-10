from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import historial_estados as schemas_historial
from app.services import historial_estados as services_historial
from app.dependencies.auth import get_current_user, RoleChecker
from app import models

router = APIRouter(
    prefix="/historial-estados",
    tags=["Historial Estados"]
)

@router.get("/", response_model=List[schemas_historial.HistorialEstadosResponse])
def obtener_todo_historial(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    return services_historial.get_all(db, skip=skip, limit=limit)

@router.get("/{historial_id}", response_model=schemas_historial.HistorialEstadosResponse)
def obtener_historial_por_id(
    historial_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    historial = services_historial.get_by_id(db, history_id=historial_id)
    if not historial:
        raise HTTPException(status_code=404, detail="Registro de historial no encontrado")

    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and historial.pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver este registro de historial."
        )
    return historial

@router.get("/pedido/{pedido_id}", response_model=List[schemas_historial.HistorialEstadosResponse])
def obtener_historial_por_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id, models.Pedido.baja == False).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver la trazabilidad de este pedido."
        )
    return services_historial.get_by_pedido_id(db, pedido_id=pedido_id)