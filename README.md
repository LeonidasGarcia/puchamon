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
7. Resolver primero los cambios de pokemon; si el rival usa `Pursuit`, interceptar la retirada antes de completar el cambio y cancelar el `switch` si el objetivo cae en ese punto.
8. Si el cambio se concreta, marcar `isRevealed = true` cuando corresponda, actualizar `activePokemonInstanceIds` y aplicar `Stealth Rock`, `Spikes` y `Toxic Spikes` en ese orden.
9. Ordenar la cola restante de movimientos por prioridad base, Velocidad efectiva y `speed tie` aleatorio cuando sea necesario.
10. Ejecutar cada movimiento validando primero si el usuario sigue con PS mayores a `0`.
11. Si el usuario sigue vivo, resolver impedimentos como `freeze`, `sleep`, `flinch`, `paralysis` y `confusion`; si puede actuar, entonces resolver `accuracy`, dano, criticos, `STAB`, efectividad de tipos y efectos secundarios inmediatos.
12. Aplicar la residual de fin de turno en este orden: clima, `Leech Seed`, `burn`, `poison` y `toxic`.
13. Actualizar el estado persistido de la batalla: `currentHp`, `status`, `volatileStatus`, `stages`, `pp`, `revealedMoves`, `fainted` y `activePokemonInstanceIds`.
14. Verificar pokemones debilitados. Si un pokemon cae y el entrenador aun tiene reserva, debe elegir uno nuevo; si la muerte ocurre en medio del turno, la cola de acciones restante continua.
15. Generar un nuevo snapshot de batalla y la lista de acciones efectivamente ejecutadas para el siguiente ciclo.

### Desglose analitico del turno

#### 1. Fase de seleccion

1. El motor espera la instruccion de ambos lados antes de avanzar.
2. En este sprint, las acciones validas son `move` y `switch`.
3. La resolucion del turno solo empieza cuando ya existen todas las decisiones requeridas para los pokemones activos.

#### 2. Fase de cambio

1. Si existe una orden de `switch`, esta fase toma prioridad absoluta sobre los movimientos del turno.
2. Primero se declara la retirada del pokemon activo. En Quinta Generacion, este es el punto en el que el contador de turnos de `sleep` se reinicia a cero.

#### 3. Determinacion del orden de accion

1. Las acciones de `move` pendientes se ordenan primero por prioridad base del movimiento.
2. Dentro del mismo grupo de prioridad, el desempate se hace por Velocidad efectiva actual, incluyendo modificadores como la reduccion por paralisis.
3. Si la Velocidad exacta es identica, el motor resuelve un `speed tie` aleatorio al `50%`.

#### 4. Ciclo de ejecucion de movimientos

1. Antes de ejecutar una accion, el motor verifica si el usuario sigue con PS mayores a `0`; si ya fue debilitado, su accion se descarta sin ejecutarse.
2. Si sigue vivo, se validan impedimentos como `freeze`, `sleep`, `flinch`, `paralysis` y `confusion`.
3. Si un estado consume el turno o `confusion` hace que el usuario se golpee a si mismo, el movimiento elegido se cancela y no produce su efecto normal.
4. Si el pokemon puede actuar, se resuelve `accuracy` comparando la precision del movimiento contra los modificadores de precision y evasion.
5. Si el movimiento impacta, se calcula el dano base aplicando `STAB`, efectividad de tipos, criticos y el resto de modificadores del momento.
6. Despues de aplicar el dano, el motor resuelve efectos secundarios inmediatos como cambios de stages, `recoil`, drenado y estados alterados.
7. Si un usuario cae por `recoil`, el debilitamiento ocurre en ese instante y afecta al resto de la cola del turno.

#### 5. Fase de resolucion residual

1. Cuando la cola de movimientos queda vacia, el motor aplica primero los ticks de clima como `sandstorm` o `hail` para los pokemones no inmunes.
2. Luego resuelve `Leech Seed`, drenando `1/8` de los PS maximos y transfiriendo ese mismo valor al ocupante rival correspondiente.
3. Despues aplica el dano residual de `burn`, `poison` y `toxic`, respetando la progresion de `toxic` turno a turno.
4. Al final de toda la residual, el motor verifica debilitamientos finales y exige reemplazos si todavia queda banca disponible.

## Arquitectura de comunicacion

- `REST` para crear la batalla, consultar snapshots, pedir historial y administrar recursos del sistema.
- `WebSocket` para la sesion activa del combate, envio de decisiones y recepcion de eventos en tiempo real.
- Esta combinacion sigue siendo valida aunque no exista multiplayer online, porque la batalla requiere un canal vivo entre frontend, motor de combate e integraciones con IA.

## Proximos pasos sugeridos

- Implementar el `BattleService` con los casos de uso del flujo anterior.
- Definir DTOs compartidos para snapshots, acciones y eventos de batalla.
- Exponer endpoints `REST` de ciclo de vida y un canal `WebSocket` exclusivo para la batalla activa.
