# Backend de Puchamon

Backend del proyecto Puchamon construido con FastAPI. Este servicio expone la base de la API y concentra la logica del dominio de batalla.

## Alcance funcional actual

- El backend debe soportar batallas `1v1`, `2v2` y `3v3`.
- Los modos iniciales son `jugador vs IA` e `IA vs IA`.
- No hay alcance de juego online ni LAN en esta etapa.
- El servidor es autoritativo: decide orden, dano, cambios de estado, clima, hazards, debilitamientos y estado final de la batalla.
- `ability`, `item` y la accion `item` aparecen en el modelo actual, pero no tienen comportamiento funcional en este sprint.

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

## Flujo tecnico de batalla

### 1. Inicio de batalla

1. Definir el tipo de batalla: `1v1`, `2v2` o `3v3`.
2. Seleccionar pokemones aleatorios para ambos entrenadores.
3. Seleccionar movesets aleatorios para todos los pokemones.
4. Calcular estadisticas reales para cada pokemon a partir de `IV`, `EV`, `BaseStats`, `Nature` y nivel.
5. Persistir `ability` e `item` como parte del estado inicial solo con valor informativo por ahora; todavia no modifican la resolucion de turnos.
6. Crear el estado inicial de `Battle` y `BattleInstance`, dejando identificados los pokemones activos por lado.

### 2. Declaracion de acciones

1. Cada entrenador declara una accion por pokemon activo.
2. Las acciones funcionales del sprint son `move` y `switch`.
3. Un `switch` consume la accion de ese pokemon en el turno y se resuelve antes que los movimientos.
4. El motor espera a tener todas las acciones necesarias antes de ejecutar el turno.

### 3. Cambio de pokemon

1. En `Battle`, se modifica `activePokemonInstanceIds` para reemplazar el pokemon activo en su mismo slot.
2. En `BattleInstance`, si el pokemon entrante no ha sido revelado, se cambia `isRevealed` a `true`.
3. Si existen hazards activos en el lado correspondiente, se aplican al entrar.

### 4. Planificacion del turno

1. Verificar si existen cambios de pokemon pendientes y ejecutarlos primero.
2. El pokemon que entra por cambio no ejecuta movimiento en ese turno.
3. Verificar restricciones por condiciones o problemas de estado antes de resolver el movimiento.
4. Si el movimiento falla por `accuracy`, no produce efecto y el movimiento se revela.
5. Si el movimiento falla por condicion o problema de estado, no produce efecto y el movimiento no se revela.
6. Para movimientos de estado, resolver stages, hazards, clima y cambios de estado segun el efecto.
7. Para movimientos fisicos o especiales, calcular dano directo y efectos secundarios segun stages, estado y probabilidades.
8. Calcular el orden final de ejecucion de acciones.

### 5. Ejecucion del turno

Durante la ejecucion se deben persistir las modificaciones sobre:

- `BattleInstance.currentHp`
- `BattleInstance.status`
- `BattleInstance.volatileStatus`
- `BattleInstance.stages`
- `BattleInstance.moveState` y `pp`
- `BattleInstance.revealedMoves`
- `BattleInstance.fainted`
- `BattleInstance.isRevealed` cuando corresponda
- `Battle.weather`
- `Battle.sides[*].hazards`
- `Battle.sides[*].activePokemonInstanceIds`

### 6. Pokemones debilitados

1. Si un pokemon se debilita, su accion pendiente futura se elimina de la cola.
2. La `BattleInstance` del pokemon debilitado se actualiza con `fainted = true`.
3. Si el entrenador tiene pokemones en reserva, debe seleccionar uno nuevo para ocupar el slot activo.
4. Si la muerte ocurre en medio del turno, la cola de movimientos restante continua despues de forzar la seleccion del reemplazo cuando corresponda.

### 7. Resultado del ciclo

Al finalizar cada turno, el backend debe producir:

- El nuevo estado de `Battle`.
- Las `BattleInstance` modificadas.
- La lista de acciones efectivamente ejecutadas en el turno.
- La informacion necesaria para determinar si la batalla continua o termina.

## REST y WebSocket

### REST

`REST` debe encargarse del ciclo de vida y la consulta de recursos. Ejemplos:

- Crear batalla.
- Obtener snapshot de una batalla.
- Consultar historial o resultado final.
- Integrar servicios auxiliares como pokedex, configuracion de IA o analitica.

### WebSocket

`WebSocket` debe encargarse de la sesion activa de combate. Ejemplos:

- Abrir un canal vivo por batalla.
- Enviar acciones declaradas por jugador o agentes de IA.
- Emitir snapshots, eventos de turno, cambios de estado y cierre de batalla.

Aunque no exista multiplayer online, `WebSocket` sigue siendo util para representar una batalla viva entre cliente, backend y agentes de IA sin depender de polling constante.
