import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from sqlalchemy import text
from . import models
from .routes import insumos, modalidades_servicio, servicios, estados, unidades_limpieza, auth, usuarios, roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    sql_file_path = os.path.join(os.path.dirname(__file__), "sql", "seed_data.sql")
    
    if os.path.exists(sql_file_path):
        try:
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            with SessionLocal() as db:
                db.execute(text(sql_script))
                db.execute(text("CALL seed_initial_laundry_data();"))
                db.commit()
            print("Seeding inicial de la base de datos completado con éxito. 🎉")
        except Exception as err:
            print(f"Error controlado en el script de inicialización: {err}")
    else:
        print(f"Archivo seed_data.sql no encontrado en: {sql_file_path}")
    yield

app = FastAPI(
    title="LavaPro API",
    description="Backend para el sistema de gestión de lavandería LavaPro",
    version="0.1.0",
    lifespan=lifespan  
)

Base.metadata.create_all(bind=engine)

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
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)

@app.get("/", tags=["Status"])
def read_root():
    return {
        "proyecto": "LavaPro API Backend",
        "estado": "Online",
        "mensaje": ("El motor de base de datos y las tablas se han inicializado correctamente.")
    }
