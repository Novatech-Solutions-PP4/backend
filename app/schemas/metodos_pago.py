from pydantic import BaseModel

class MetodoPagoBase(BaseModel):
    nombre: str

class MetodoPagoCreate(MetodoPagoBase):
    pass

class MetodoPagoResponse(MetodoPagoBase):
    id: int

    class Config:
        from_attributes = True
