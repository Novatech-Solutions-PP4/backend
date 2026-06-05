from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.utils import security
from app.services import usuarios as services_usuarios
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de inicio de sesión.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = security.verify_token(token)
    if payload is None:
        raise credentials_exception
        
    usuario_id: str = payload.get("sub")
    if usuario_id is None:
        raise credentials_exception
        
    usuario = services_usuarios.get_by_id(db, usuario_id=int(usuario_id))
    
    if not usuario.cuenta_activa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El acceso ha sido denegado. Esta cuenta de usuario no está activa."
        )
        
    return usuario


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.Usuario = Depends(get_current_user)) -> models.Usuario:
        if current_user.rol.nombre not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Acción reservada para los roles: {', '.join(self.allowed_roles)}."
            )
        return current_user