from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import usuarios as schemas_usuarios
from app.services import usuarios as services_usuarios
from app.utils import security

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/activar-cuenta", response_model=schemas_usuarios.UsuarioResponse)
def activar_cuenta(datos: schemas_usuarios.UsuarioActivar, db: Session = Depends(get_db)):
    return services_usuarios.activate_account(db=db, datos_activacion=datos)

@router.post("/login")
def login(credenciales: schemas_usuarios.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = services_usuarios.get_by_email(db, email_str=credenciales.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o el usuario no existe."
        )

    if not usuario.cuenta_activa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no está activa. Por favor, verifique su email para activarla."
        )

    if not security.verify_password(credenciales.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas."
        )

    token_payload = {
        "sub": str(usuario.id),
        "rol": usuario.rol.nombre
    }
    access_token = security.create_access_token(data=token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "rol": usuario.rol.nombre,
            "dni": usuario.dni,
            "telefono": usuario.telefono,
            "codigo_qr": usuario.codigo_qr
        }
    }

@router.post("/forgot-password")
async def solicitar_recuperacion(datos: schemas_usuarios.UsuarioForgotPassword, db: Session = Depends(get_db)):
    return await services_usuarios.request_password_reset(db=db, email_str=datos.email)

@router.post("/reset-password")
def confirmar_recuperacion(datos: schemas_usuarios.UsuarioResetPassword, db: Session = Depends(get_db)):
    return services_usuarios.reset_password(db=db, datos_reset=datos)