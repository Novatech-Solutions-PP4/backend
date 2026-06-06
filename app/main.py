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
                insumos_data = [
                    {"nombre": "Detergente Industrial", "cantidad": 450.0, "cantidad_alerta": 100.0, "costo_actual": 2455.0},
                    {"nombre": "Suavizante Premium", "cantidad": 98.0, "cantidad_alerta": 100.0, "costo_actual": 18450.0},
                    {"nombre": "Quita Manchas Activo", "cantidad": 14.0, "cantidad_alerta": 10.0, "costo_actual": 5100.0}
                ]
                seeded_insumos = {}
                for ins_data in insumos_data:
                    ins = db.query(models.Insumo).filter(models.Insumo.nombre == ins_data["nombre"]).first()
                    if not ins:
                        ins = models.Insumo(
                            nombre=ins_data["nombre"],
                            cantidad=ins_data["cantidad"],
                            cantidad_alerta=ins_data["cantidad_alerta"],
                            costo_actual=ins_data["costo_actual"]
                        )
                        db.add(ins)
                        db.flush()
                    seeded_insumos[ins_data["nombre"]] = ins
                unidades = {u.nombre: u.id for u in db.query(models.UnidadLimpieza).all()}
                modalidades = {m.nombre: m.id for m in db.query(models.ModalidadServicio).all()}
                servicios_data = [
                    {
                        "nombre": "Lavado Canasto Económico",
                        "precio": 4000.0,
                        "unidad": "Canasto",
                        "modalidad": "Económico",
                        "insumos": [("Detergente Industrial", 200.0)]
                    },
                    {
                        "nombre": "Limpieza Acolchado Estándar",
                        "precio": 13730.0,
                        "unidad": "Acolchado",
                        "modalidad": "Standar",
                        "insumos": [("Detergente Industrial", 250.0), ("Suavizante Premium", 150.0), ("Quita Manchas Activo", 50.0)]
                    },
                    {
                        "nombre": "Lavado Calzado Especial",
                        "precio": 4500.0,
                        "unidad": "Calzado",
                        "modalidad": "Delicado",
                        "insumos": [("Detergente Industrial", 100.0), ("Quita Manchas Activo", 30.0)]
                    }
                ]
                for serv_data in servicios_data:
                    serv = db.query(models.Servicio).filter(models.Servicio.nombre == serv_data["nombre"]).first()
                    id_uni = unidades.get(serv_data["unidad"])
                    id_mod = modalidades.get(serv_data["modalidad"])
                    if id_uni and id_mod:
                        if not serv:
                            serv = models.Servicio(
                                nombre=serv_data["nombre"],
                                precio=serv_data["precio"],
                                id_unidad_limpieza=id_uni,
                                id_modalidad=id_mod
                            )
                            db.add(serv)
                            db.flush()
                            for ins_name, qty in serv_data["insumos"]:
                                ins_obj = seeded_insumos.get(ins_name)
                                if ins_obj:
                                    assoc = models.InsumosServicios(
                                        id_servicio=serv.id,
                                        id_insumo=ins_obj.id,
                                        cantidad_utilizada=qty
                                    )
                                    db.add(assoc)
                db.commit()
            print("Seeding inicial de insumos y servicios completado con éxito. 🎉")
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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://app.lavapro.online",
        "https://api.lavapro.online"
    ],
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)?lavapro\.online(:[0-9]+)?$",
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
        "mensaje": "El motor de base de datos y las tablas se han inicializado correctamente."
    }
