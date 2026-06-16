# NovaTech Solutions - Backend

Backend del sistema de gestión desarrollado por **NovaTech Solutions** para el Proyecto Integrador del Instituto de Formación Técnica Superior N°29.

## Descripción

Este repositorio contiene la aplicación backend del sistema Lavapro, desarrollada con FastAPI, SQLAlchemy y UV. La API permite la conexión entre el frontend y la base de datos, facilitando las operaciones para gestionar y manipular datos en la base de datos.

## Acceso a la aplicación

La versión desplegada de la API se encuentra disponible en:

**https://app.lavapro.online**


## Tecnologías utilizadas

* FastAPI
* UV
* SQLAlchemy
* Python
* PostgreSQL
* Docker

## Estructura del proyecto

```text
src/
└── app/
    ├── routes/
    ├── schemas/
    ├── services/
    ├── database.py
    ├── main.py
    └── models.py
```

# Configuración

- Instalar python y uv
- Crear entorno virtual: `uv venv`
- Activar entorno virtual: `source .venv/bin/activate`
- Instalar dependencias: `uv sync`
- Ejecutar docker compose: `docker-compose up -d`
- Ejecutar psql: `docker exec -it lavapro-db psql -U lavapro -d lavapro_api`
- Ejecutar servidor backend: `fastapi dev app/main.py`

# Procedimientos almacenados y docker

Volver a registrar el procedimiento almacenado con nuevos cambios: `docker compose exec -T db psql -U lavapro -d lavapro_api < app/sql/seed_data.sql`

## Equipo de desarrollo

NovaTech Solutions

* Santiago Avalos
* Leandro Bilokapic
* Martín Giménez Gaitán
* Santiago Paguaga
* Damián Toledo

## Institución

Instituto de Formación Técnica Superior N°29

## Estado

Proyecto académico en desarrollo.

