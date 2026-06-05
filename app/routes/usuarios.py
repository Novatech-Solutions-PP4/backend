from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import usuarios as schemas_usuarios
from app.services import usuarios as services_usuarios

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=schemas_usuarios.UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: schemas_usuarios.UsuarioCreate, db: Session = Depends(get_db)):
    return await services_usuarios.create(db=db, usuario=usuario)

@router.get("/", response_model=List[schemas_usuarios.UsuarioResponse])
def obtener_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services_usuarios.get_all(db, skip=skip, limit=limit)

@router.get("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def obtener_usuario_por_id(usuario_id: int, db: Session = Depends(get_db)):
    return services_usuarios.get_by_id(db, usuario_id=usuario_id)

@router.patch("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def actualizar_usuario(usuario_id: int, usuario: schemas_usuarios.UsuarioUpdate, db: Session = Depends(get_db)):
    return services_usuarios.update(db, usuario_id=usuario_id, usuario_data=usuario)

@router.delete("/{usuario_id}", response_model=schemas_usuarios.UsuarioResponse)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return services_usuarios.delete(db, usuario_id=usuario_id)