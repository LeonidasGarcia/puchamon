# Puchamon

Proyecto universitario inspirado en Pokemon Showdown con enfoque en simulacion de batallas Pokemon y soporte para automatizacion con IA.

## Estructura del repositorio

- `backend/`: API en Python con FastAPI.
- `frontend/`: espacio reservado para la interfaz cliente.
- `docs/`: documentacion funcional y tecnica del proyecto.

## Estado actual

Actualmente el backend es la parte mas avanzada del repositorio. `frontend/` y `docs/` existen como base para organizar el desarrollo posterior.

## Alcance actual de batalla

- Tipos de batalla previstos: `1v1`, `2v2` y `3v3`.
- Modos previstos en esta etapa: `jugador vs IA` e `IA vs IA`.
- No se contempla juego online ni LAN en esta fase.
- La batalla debe construirse sobre un servidor autoritativo: el cliente y la IA solo envian decisiones; el backend resuelve el estado real del combate.
- `ability` e `item` existen en el modelo de datos actual, pero no tienen efecto funcional en este sprint.

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

## Flujo de batalla propuesto

1. Crear la batalla definiendo el tipo de enfrentamiento: `1v1`, `2v2` o `3v3`.
2. Generar para ambos entrenadores un conjunto aleatorio de pokemones y movesets.
3. Calcular para cada pokemon sus estadisticas reales a partir de `IV`, `EV`, `BaseStats`, `Nature` y nivel.
4. Los datos de `ability` e `item` pueden persistirse junto al pokemon o moveset, pero no participan todavia en la resolucion del combate.
5. Marcar los pokemones iniciales activos y preparar el estado inicial de `Battle` y `BattleInstance`.
6. Esperar a que cada entrenador declare las acciones de sus pokemones activos antes de resolver el turno.
7. Resolver primero los cambios de pokemon; si entra un pokemon no revelado, se marca `isRevealed = true`, se actualiza `activePokemonInstanceIds` y se aplican hazards si existen.
8. Para movimientos, validar primero restricciones de estado; si el pokemon falla por `accuracy`, el movimiento se revela; si no actua por una condicion o problema de estado, el movimiento no se revela.
9. Calcular el orden de accion y ejecutar efectos de estado, clima, hazards, stages y dano directo segun corresponda.
10. Actualizar el estado persistido de la batalla: `currentHp`, `status`, `volatileStatus`, `stages`, `pp`, `revealedMoves`, `fainted`, `weather`, `sides[*].hazards` y `activePokemonInstanceIds`.
11. Verificar pokemones debilitados. Si un pokemon cae y el entrenador aun tiene reserva, debe elegir uno nuevo; si la muerte ocurre en medio del turno, la cola de acciones restante continua.
12. Generar un nuevo snapshot de batalla y la lista de acciones efectivamente ejecutadas para el siguiente ciclo.

## Arquitectura de comunicacion

- `REST` para crear la batalla, consultar snapshots, pedir historial y administrar recursos del sistema.
- `WebSocket` para la sesion activa del combate, envio de decisiones y recepcion de eventos en tiempo real.
- Esta combinacion sigue siendo valida aunque no exista multiplayer online, porque la batalla requiere un canal vivo entre frontend, motor de combate e integraciones con IA.

## Proximos pasos sugeridos

- Implementar el `BattleService` con los casos de uso del flujo anterior.
- Definir DTOs compartidos para snapshots, acciones y eventos de batalla.
- Exponer endpoints `REST` de ciclo de vida y un canal `WebSocket` exclusivo para la batalla activa.
