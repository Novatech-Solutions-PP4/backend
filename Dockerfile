FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

COPY pyproject.toml ./

RUN uv sync --no-cache

COPY ./app ./app

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]