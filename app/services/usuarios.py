from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app import models
from app.schemas import usuarios as schemas_usuarios
from app.utils import security, email

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario)\
             .options(joinedload(models.Usuario.rol))\
             .filter(models.Usuario.baja == False)\
             .offset(skip).limit(limit).all()


def get_by_id(db: Session, usuario_id: int):
    db_usuario = db.query(models.Usuario)\
                   .options(joinedload(models.Usuario.rol))\
                   .filter(models.Usuario.id == usuario_id, models.Usuario.baja == False)\
                   .first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el usuario con el ID {usuario_id} o no está disponible."
        )
    return db_usuario


def get_by_email(db: Session, email_str: str):
    return db.query(models.Usuario)\
             .options(joinedload(models.Usuario.rol))\
             .filter(models.Usuario.email == email_str, models.Usuario.baja == False)\
             .first()


async def create(db: Session, usuario: schemas_usuarios.UsuarioCreate):
    if db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya se encuentra registrado en el sistema."
        )
        
    if db.query(models.Usuario).filter(models.Usuario.dni == usuario.dni).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El DNI ya se encuentra registrado en el sistema."
        )

    if not db.query(models.Rol).filter(models.Rol.id == usuario.id_rol).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear usuario: El Rol con ID {usuario.id_rol} no existe."
        )

    datos_usuario = usuario.model_dump()
    
    password_temporal = security.generate_random_string()
    datos_usuario["password"] = security.get_password_hash(password_temporal)
    datos_usuario["cuenta_activa"] = False
    datos_usuario["password_cambiada"] = False
    datos_usuario["baja"] = False

    nuevo_usuario = models.Usuario(**datos_usuario)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_usuario.codigo_qr = f"LAVAPRO-USR-{nuevo_usuario.id}-{nuevo_usuario.dni}"
    db.commit()
    db.refresh(nuevo_usuario)

    token_payload = {"sub": str(nuevo_usuario.id), "action": "activate"}
    token_activacion = security.create_access_token(
        data=token_payload, 
        expires_delta=security.timedelta(hours=48)
    )

    try:
        await email.send_activation_email(
            to_email=nuevo_usuario.email,
            nombre_usuario=f"{nuevo_usuario.nombre} {nuevo_usuario.apellido}",
            token=token_activacion
        )
    except Exception as err:
        print(f"Error al despachar email de activación: {err}")

    return nuevo_usuario


def update(db: Session, usuario_id: int, usuario_data: schemas_usuarios.UsuarioUpdate):
    db_usuario = get_by_id(db, usuario_id)
    datos_actualizar = usuario_data.model_dump(exclude_unset=True)

    if "email" in datos_actualizar and datos_actualizar["email"] != db_usuario.email:
        if db.query(models.Usuario).filter(models.Usuario.email == datos_actualizar["email"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo email ya pertenece a otro usuario."
            )

    if "dni" in datos_actualizar and datos_actualizar["dni"] != db_usuario.dni:
        if db.query(models.Usuario).filter(models.Usuario.dni == datos_actualizar["dni"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo DNI ya pertenece a otro usuario."
            )

    if "id_rol" in datos_actualizar and datos_actualizar["id_rol"] != db_usuario.id_rol:
        if not db.query(models.Rol).filter(models.Rol.id == datos_actualizar["id_rol"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El Rol con ID {datos_actualizar['id_rol']} no existe."
            )

    for key, value in datos_actualizar.items():
        setattr(db_usuario, key, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def activate_account(db: Session, datos_activacion: schemas_usuarios.UsuarioActivar):
    payload = security.verify_token(datos_activacion.token)
    if not payload or payload.get("action") != "activate":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de activación es inválido o ha expirado de forma segura."
        )

    if len(datos_activacion.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de registro: La contraseña suministrada debe contener al menos 8 caracteres."
        )

    usuario_id = int(payload.get("sub"))
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id, models.Usuario.baja == False).first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario asociado a este token de activación no existe."
        )

    if db_usuario.cuenta_activa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta ya fue activada previamente en la plataforma."
        )

    db_usuario.password = security.get_password_hash(datos_activacion.password)
    db_usuario.cuenta_activa = True
    db_usuario.password_cambiada = True

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


async def request_password_reset(db: Session, email_str: str):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email_str, models.Usuario.baja == False).first()
    
    if usuario and usuario.cuenta_activa:
        token_payload = {"sub": str(usuario.id), "action": "reset"}
        token_reset = security.create_access_token(
            data=token_payload,
            expires_delta=security.timedelta(hours=2)
        )
        try:
            await email.send_reset_password_email(
                to_email=usuario.email,
                nombre_usuario=f"{usuario.nombre} {usuario.apellido}",
                token=token_reset
            )
        except Exception as err:
            print(f"Error al despachar email de recuperación: {err}")
            
    return {"message": "Si el correo electrónico se encuentra registrado, recibirás un enlace de recuperación a la brevedad."}


def reset_password(db: Session, datos_reset: schemas_usuarios.UsuarioResetPassword):
    payload = security.verify_token(datos_reset.token)
    if not payload or payload.get("action") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de recuperación es inválido, ha expirado o ya fue utilizado."
        )

    usuario_id = int(payload.get("sub"))
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id, models.Usuario.baja == False).first()
    
    if not db_usuario or not db_usuario.cuenta_activa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario asociado a esta solicitud ya no se encuentra disponible."
        )

    db_usuario.password = security.get_password_hash(datos_reset.password)
    db_usuario.password_cambiada = True
    
    db.commit()
    db.refresh(db_usuario)
    return {"message": "Tu contraseña ha sido restablecida con éxito. Ya podés iniciar sesión."}


def delete(db: Session, usuario_id: int):
    db_usuario = get_by_id(db, usuario_id)
    db_usuario.baja = True
    db_usuario.cuenta_activa = False  
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario