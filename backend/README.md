# Backend de Puchamon

Backend del proyecto Puchamon construido con FastAPI. Este servicio expone la base de la API y concentra la logica del dominio de batalla.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic Settings
- Loguru
- Pytest

## Requisitos

- Tener `uv` instalado.
- Usar Python `3.12`.
- Definir estas variables de entorno:
  - `DATABASE_URI`
  - `DATABASE_NAME`

## Instalacion

```bash
uv sync
```

## Ejecucion local

```bash
uv run start
```

La aplicacion arranca en `http://localhost:8000`.

## Desarrollo

Ejecutar pruebas:

```bash
uv run pytest
```
