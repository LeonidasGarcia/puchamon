# Puchamon

Proyecto universitario inspirado en Pokemon Showdown con enfoque en simulacion de batallas 3v3 o 4v4 y soporte futuro para automatizacion con IA.

## Estructura del repositorio

- `backend/`: API en Python con FastAPI.
- `frontend/`: espacio reservado para la interfaz cliente.
- `docs/`: documentacion funcional y tecnica del proyecto.

## Estado actual

Actualmente el backend es la parte mas avanzada del repositorio. `frontend/` y `docs/` existen como base para organizar el desarrollo posterior.

## Inicio rapido

1. Entra en `backend/`.
2. Instala dependencias con `uv sync`.
3. Configura las variables de entorno requeridas en `.env`.
4. Inicia la API con `uv run start`.

## Datos de Pokemon en MongoDB
El archivo `frontend/pokemon.js` permite cargar datos iniciales en MongoDB para el proyecto.
1. Asegurate de tener MongoDB en ejecucion.
2. Asegurate de tener `mongosh` instalado.
3. Desde la raiz del proyecto, ejecuta `mongosh frontend/pokemon.js`.
Los datos se cargaran en la base `pokemon_battle_db`.

## Proximos pasos sugeridos

- Implementar la interfaz web del simulador.
- Documentar reglas de batalla, arquitectura y flujo del sistema.
- Integrar los modulos de IA sobre el motor de combate.
