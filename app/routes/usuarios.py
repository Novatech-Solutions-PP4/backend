from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import usuarios as schemas_usuarios
from app.services import usuarios as services_usuarios
from app.dependencies.auth import get_current_user, RoleChecker
from app import models

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=schemas_usuarios.UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    usuario: schemas_usuarios.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    if current_user.rol.nombre.lower() == "operador":
        rol_cliente = db.query(models.Rol).filter(models.Rol.nombre.ilike("Cliente")).first()
        id_rol_cliente = rol_cliente.id if rol_cliente else 3
        if usuario.id_rol != id_rol_cliente:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Un operador solo tiene permisos para registrar usuarios con el rol de Cliente."
            )

    return await services_usuarios.create(db=db, usuario=usuario)

@router.get("/", response_model=List[schemas_usuarios.UsuarioResponse])
def obtener_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"]))
):
    return services_usuarios.get_all(db, skip=skip, limit=limit)

@router.get("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def obtener_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    is_staff = current_user.rol.nombre in ["Administrador", "Operador"]
    if not is_staff and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver este perfil."
        )
    db_usuario = services_usuarios.get_by_id(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.patch("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario: schemas_usuarios.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    is_admin = current_user.rol.nombre == "Administrador"
    is_operator = current_user.rol.nombre == "Operador"

    if not is_admin and current_user.id != usuario_id:
        target_user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id, models.Usuario.baja == False).first()
        if not (is_operator and target_user and target_user.rol.nombre.lower() == "cliente"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes para modificar este perfil."
            )

    if not is_admin and usuario.id_rol is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede modificar el rol de un usuario."
        )

    db_usuario = services_usuarios.update(db, usuario_id=usuario_id, usuario_data=usuario)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.delete("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(RoleChecker(["Administrador"]))
):
    db_usuario = services_usuarios.delete(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario