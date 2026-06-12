# backend test

# Set up
- Install python and uv
- Create virtual environment: ```uv venv```
- Activate virtual environment: ```source .venv/bin/activate```
- Install dependencies: ```uv sync```
- Run docker compose: ```docker-compose up -d```
- Run psql: ```docker exec -it lavapro-db psql -U lavapro -d lavapro_api```
- Run backend server: ```fastapi dev app/main.py```
# Stored procedures and docker
Re-register the stored procedure with the new changes: ```docker compose exec -T db psql -U lavapro -d lavapro_api < app/sql/seed_data.sql```
