from pydantic import BaseModel
from typing import Optional

class RolBase(BaseModel):
    nombre: str

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre: Optional[str] = None

class RolResponse(RolBase):
    id: int

    class Config:
        from_attributes = True