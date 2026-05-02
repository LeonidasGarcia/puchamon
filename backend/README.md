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

### 2. Declaracion de acciones e input

1. Cada entrenador declara una accion por pokemon activo.
2. Las acciones funcionales del sprint son `move` y `switch`.
3. Un `switch` consume la accion de ese pokemon en el turno y se resuelve antes que los movimientos.
4. El motor espera a tener todas las acciones necesarias antes de ejecutar el turno.

### 3. Cambio de pokemon y hazards

1. Si existe una orden de `switch`, entra en una fase de pre-accion con prioridad absoluta.
2. El pokemon activo se marca para retirarse. En Quinta Generacion, este es el instante exacto en el que el contador de turnos de `sleep` se reinicia a cero.
3. Antes de completar la salida, el motor debe verificar si el rival eligio `Pursuit`.
4. Si `Pursuit` intercepta la retirada, se ejecuta inmediatamente antes del cambio con potencia base doblada a `80`.
5. Si el objetivo cae por la intercepcion de `Pursuit`, el `switch` original se cancela y el reemplazo pasa a ser un ingreso por debilitacion.
6. Si el cambio continua, en `Battle` se actualiza `activePokemonInstanceIds` para reemplazar el pokemon activo en su mismo slot.
7. En `BattleInstance`, si el pokemon entrante no ha sido revelado, se cambia `isRevealed` a `true`.
8. Luego se aplican hazards al entrar en este orden fijo: `Stealth Rock`, `Spikes`, `Toxic Spikes`.
9. `Stealth Rock` usa `1/8` de los PS maximos multiplicado por la efectividad de tipo roca sobre el objetivo.
10. `Spikes` solo afecta a objetivos que tocan el suelo y resta `1/8`, `1/6` o `1/4` de los PS maximos segun el numero de capas.
11. `Toxic Spikes` solo afecta a objetivos que tocan el suelo; con `1` capa aplica `poison`, con `2` capas aplica `toxic`, y un pokemon de tipo veneno elimina las capas al entrar.

### 4. Determinacion del orden de accion

1. Una vez resueltos todos los `switch`, el pokemon que entro por cambio no ejecuta movimiento en ese mismo turno.
2. La cola restante se ordena primero por prioridad base del movimiento.
3. Dentro del mismo nivel de prioridad, el desempate se hace por Velocidad efectiva actual del usuario.
4. La Velocidad efectiva debe reflejar cambios de stages y penalizaciones como la reduccion por paralisis.
5. Si ambos pokemones empatan en Velocidad exacta, el orden se decide con un `speed tie` aleatorio al `50%`.

### 5. Ejecucion del turno

1. El motor itera sobre la cola de acciones ya ordenada.
2. Antes de cualquier otra validacion, se comprueba si el usuario sigue con PS mayores a `0`.
3. Si el pokemon ya fue debilitado por una accion previa del mismo turno, su accion se descarta por completo.
4. Si sigue vivo, se resuelven impedimentos de accion como `freeze`, `sleep`, `flinch`, `paralysis` y `confusion`.
5. Si `confusion` hace que el usuario se golpee a si mismo, el movimiento elegido se cancela y se calcula el autogolpe como dano fisico de potencia `40` sin tipo contra el propio usuario.
6. Si el pokemon supera esas validaciones, el movimiento avanza al chequeo de `accuracy`.
7. Si falla por `accuracy`, no produce efecto y el movimiento se revela.
8. Si falla por condicion o problema de estado antes de actuar, no produce efecto y el movimiento no se revela.
9. Si impacta, se calcula el dano aplicando `STAB`, efectividad de tipos, criticos y el resto de modificadores del momento.
10. En Quinta Generacion, un critico debe ignorar las bajadas de ataque del usuario y las subidas de defensa del objetivo cuando corresponda.
11. Despues de restar PS al objetivo, se resuelven efectos secundarios inmediatos como cambios de stages, `recoil`, drenado y aplicacion de estados alterados.
12. Si el usuario cae por `recoil`, el debilitamiento ocurre en ese instante y afecta a la cola restante del turno.

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

### 6. Resolucion residual de fin de turno

1. Cuando la cola de movimientos queda vacia, el motor aplica primero los ticks de clima como `sandstorm` o `hail` para todos los pokemones no inmunes.
2. Luego resuelve `Leech Seed`, drenando `1/8` de los PS maximos del afectado y transfiriendo ese mismo valor al ocupante rival correspondiente.
3. Despues aplica los ticks de `burn`, `poison` y `toxic` en ese orden logico de residual, respetando la progresion acumulativa de `toxic`.
4. Una vez cerrada la residual, el motor hace una validacion final de debilitamientos antes de terminar el turno.
5. Si un reemplazo entra por un debilitamiento de final de turno, sus hazards se resuelven inmediatamente antes de aceptar nuevas acciones del siguiente ciclo.

### 7. Pokemones debilitados

1. Si un pokemon se debilita, su accion pendiente futura se elimina de la cola.
2. La `BattleInstance` del pokemon debilitado se actualiza con `fainted = true`.
3. Si el entrenador tiene pokemones en reserva, debe seleccionar uno nuevo para ocupar el slot activo.
4. Si la muerte ocurre en medio del turno, la cola de movimientos restante continua despues de forzar la seleccion del reemplazo cuando corresponda.

### 8. Resultado del ciclo

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
