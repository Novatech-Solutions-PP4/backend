from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LavaPro API",
    description="Backend para el sistema de gestión de lavandería LavaPro",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Status"])
def read_root():
    return {
        "proyecto": "LavaPro API Backend",
        "estado": "Online",
        "mensaje": "El motor de base de datos y las tablas se han inicializado correctamente."
    }