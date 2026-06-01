import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from sqlalchemy import text
from . import models
from .routes import insumos
from .routes import modalidades_servicio
from .routes import servicios
from .routes import estados
from .routes import unidades_limpieza

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def run_db_seeding():
    sql_file_path = os.path.join(os.path.dirname(__file__), "sql", "seed_data.sql")
    
    if os.path.exists(sql_file_path):
        try:
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            with engine.connect() as connection:
                connection.execute(text(sql_script))
                connection.execute(text("CALL seed_initial_laundry_data();"))
                connection.commit()
        except Exception as e:
            print(f"Error controlado en el script de inicialización: {e}")
    else:
        print(f"Archivo seed_data.sql no encontrado en: {sql_file_path}")

app = FastAPI(
    title="LavaPro API",
    description="Backend para el sistema de gestión de lavandería LavaPro",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)?lavapro\.online$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insumos.router)
app.include_router(modalidades_servicio.router)
app.include_router(servicios.router)
app.include_router(estados.router)
app.include_router(unidades_limpieza.router)

@app.get("/", tags=["Status"])
def read_root():
    return {
        "proyecto": "LavaPro API Backend",
        "estado": "Online",
        "mensaje": ("El motor de base de datos y las tablas se han inicializado correctamente.")
    }
