import os
from urllib.parse import urlparse
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routes import insumos

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LavaPro API",
    description="Backend para el sistema de gestión de lavandería LavaPro",
    version="0.1.0"
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    if not origin:
        raise HTTPException(status_code=403, detail="Origin requerido")

    parsed = urlparse(origin)

    hostname = parsed.hostname or ""

    is_valid_origin = (parsed.scheme == "https" and (hostname == "lavapro.online" or hostname.endswith(".lavapro.online")))

    if not is_valid_origin:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)?lavapro\.online$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insumos.router)

@app.get("/", tags=["Status"])
def read_root():
    return {
        "proyecto": "LavaPro API Backend",
        "estado": "Online",
        "mensaje": ("El motor de base de datos y las tablas se han inicializado correctamente.")
    }