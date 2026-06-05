from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from app.schemas.roles import RolResponse

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    email: str  
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    id_rol: int

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    cuenta_activa: Optional[bool] = None
    baja: Optional[bool] = None
    id_rol: Optional[int] = None

class UsuarioActivar(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validar_password_longitud(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener un mínimo de 8 caracteres.")
        return v

class UsuarioLogin(BaseModel):
    email: str
    password: str

class UsuarioForgotPassword(BaseModel):
    email: EmailStr

class UsuarioResetPassword(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validar_password_longitud(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La nueva contraseña debe tener un mínimo de 8 caracteres.")
        return v

class UsuarioResponse(UsuarioBase):
    id: int
    password_cambiada: bool
    cuenta_activa: bool
    baja: bool
    codigo_qr: Optional[str] = None
    rol: RolResponse  

    class Config:
        from_attributes = True