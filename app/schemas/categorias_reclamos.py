from pydantic import BaseModel
from typing import Optional

class CategoriaReclamoBase(BaseModel):
    nombre: str

class CategoriaReclamoCreate(CategoriaReclamoBase):
    pass

class CategoriaReclamoUpdate(BaseModel):
    nombre: Optional[str] = None

class CategoriaReclamoResponse(CategoriaReclamoBase):
    id: int

    class Config:
        from_attributes = True
