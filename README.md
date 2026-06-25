# Puchamon

El núcleo de este proyecto no es solo la simulación del combate, sino **la Inteligencia Artificial**. El sistema está diseñado como un entorno de experimentación (*sandbox*) para probar diferentes aproximaciones algorítmicas en la toma de decisiones, desde agentes puramente aleatorios hasta sistemas de búsqueda competitiva (Minimax) optimizados con Algoritmos Genéticos.

El motor de combate está basado en un servidor autoritativo que resuelve el estado real del combate de forma determinista. De esta manera, se garantiza que tanto las diferentes heurísticas de IA como los jugadores humanos se enfrenten bajo exactamente las mismas reglas, mecánicas y condiciones de información.

## 🏗 Arquitectura del Proyecto

El proyecto está dividido en tres directorios principales:

- `backend/`: API desarrollada en Python 3.12 con **FastAPI**. Contiene la lógica central del motor de batalla (autoritativo), modelos de dominio, validación de turnos y conexión con la base de datos. Es el foco principal de desarrollo actualmente.
- `frontend/`: Aplicación cliente desarrollada con **React + Vite + TypeScript**. (Actualmente en fase base/placeholder).

### Comunicación
- **REST**: Para la creación de la batalla, definir el enfrentamiento, consultar snapshots del estado, obtener historial y administrar recursos.
- **WebSocket**: Para la sesión activa del combate. Facilita el envío de decisiones de turno y la recepción de eventos en tiempo real. Esta combinación es vital para mantener un canal vivo entre frontend, motor de combate e integraciones con IA.

## ⚔️ Características del Sistema de Batalla

- **Formatos soportados:** `1v1`, `2v2` y `3v3`.
- **Modos de juego:** Jugador vs IA, e IA vs IA. (No se contempla multijugador online o LAN en esta fase).
- **Servidor Autoritativo:** El cliente y la IA únicamente envían sus decisiones (`move` o `switch`). El backend resuelve y es dueño absoluto de la verdad del estado de la partida.
- **Modelo de datos:** Las propiedades `ability` e `item` existen en el modelo de datos, pero en esta etapa aún no tienen efecto funcional en la resolución del combate.

## 🧠 Inteligencia Artificial y Dificultades (El Core del Proyecto)

Dado que el foco principal del proyecto es la investigación y aplicación de IA en combates por turnos con información imperfecta, el sistema de toma de decisiones (`ActionSelector` en `backend/src/puchamon/modules/agentia/`) implementa varios niveles de dificultad utilizando distintos enfoques algorítmicos. 

Una característica arquitectónica vital es que el árbol de decisiones evalúa de forma unificada **tanto los ataques como los cambios de Pokémon (switches)**. Esto permite a la IA hacer retiradas tácticas preventivas en lugar de solo reaccionar (switch forzado) cuando un Pokémon es debilitado.

Los niveles de IA implementados actualmente son:

- **Nivel 1 (Fácil) - `RandomActionSelector`:**
  Agente base. Evalúa las acciones legalmente disponibles en ese turno (movimientos con PP restantes y cambios a Pokémon no debilitados) y selecciona una de manera totalmente aleatoria. Su propósito es servir como *baseline* estadístico para medir el rendimiento de los modelos superiores.

- **Nivel 2 (Medio) - Minimax (Heurística Básica):**
  Implementa el algoritmo **Minimax con Poda Alpha-Beta** (`MinimaxActionSelector`). Explora el árbol de decisiones simulando las transiciones de estado a futuro usando el motor de batalla real. Su función heurística (`evaluate_level_2`) es muy directa y prioriza causar daño inmediato y mantener la ventaja de vida.
  > **Fórmula:** `Score = (% HP Total del Equipo IA) - (% HP del Pokémon Activo Rival)`

- **Nivel 3 (Difícil Manual) - Minimax (Heurística Avanzada):**
  Usa el mismo motor de búsqueda Minimax, pero su función de evaluación (`evaluate_level_3_manual`) es más profunda y de corte "experto". Analiza proyecciones de desgaste a mediano plazo, prioriza la conservación de amenazas ofensivas y evalúa el riesgo.
  > **Fórmula:** `Score = Σ (wi * factor_i)` donde cada factor `i` ∈ `[-1, 1]` y la suma de pesos `w` es `1.0`.
  > Los 7 factores evaluados son diferenciales (IA vs Rival) en:
  > 1. `HP` (Ventaja de PS)
  > 2. `Alive` (Diferencia de Pokémon vivos)
  > 3. `Damage` (Diferencial de presión ofensiva calculando daño proyectado)
  > 4. `Type` (Diferencial de efectividad de tipos)
  > 5. `Speed` (Control de velocidad / Speed ties)
  > 6. `Status` (Penalización por estados alterados como quemadura o parálisis)
  > 7. `Effects` (Utilidad de efectos secundarios y movimientos de estado)
  > *Los pesos (`w`) fueron sintonizados manualmente basándose en fundamentos de metajuego.*

- **Nivel 4 (Difícil GA) - Minimax optimizado con Algoritmos Genéticos:**
  Es el pináculo de dificultad del proyecto. Mantiene la profundidad, el motor Minimax y **la misma fórmula diferencial de 7 factores** del Nivel 3, pero **sus pesos (`w`) fueron descubiertos y ajustados mediante Algoritmos Genéticos (GA)** (`evaluate_level_3_ga`). 
  Este agente fue entrenado iterando miles de simulaciones en un entorno puramente "IA vs IA". A través de la evolución y cruzamiento de los mejores cromosomas (pesos), el algoritmo encontró balances matemáticos óptimos y contraintuitivos que maximizan el *win rate*, aprendiendo automáticamente a castigar cambios y predecir las jugadas del rival de manera emergente.

## 🚀 Guía de Inicio Rápido (Setup)

### Requisitos Previos
- **Python 3.12** y [uv](https://docs.astral.sh/uv/) instalados.
- **Node.js** y npm instalados.
- **MongoDB** en ejecución.
- **Mongosh** (MongoDB Shell) instalado.

### 1. Carga de Base de Datos

El sistema requiere la carga inicial de información de Pokémon en MongoDB.

1. Asegúrate de tener MongoDB en ejecución y `mongosh` instalado.
2. Desde la raíz del proyecto, ejecuta:
   ```bash
   mongosh frontend/pokemon.js
   ```
Esto cargará los datos iniciales en la base de datos `puchamon`.

### 2. Backend (Python / FastAPI)

1. Ingresa al directorio del backend:
   ```bash
   cd backend
   ```
2. Instala las dependencias con `uv`:
   ```bash
   uv sync
   ```
3. Crea un archivo `.env` en el directorio `backend/` con las variables de base de datos requeridas:
   ```env
   DATABASE_URI="mongodb://localhost:27017/"
   DATABASE_NAME="puchamon"
   ```
4. Inicia el servidor:
   ```bash
   uv run start
   ```
   El servidor arrancará en `http://localhost:8000`.

**Comandos adicionales del Backend:**
- **Ejecutar tests:** `uv run pytest` (Usa `asyncio_mode = "auto"`, los tests van en la carpeta `tests/`).
- **Linter:** `uv run ruff check .` (Ruff está configurado en `pyproject.toml` con `line-length 150` y estilo `Google docstrings`. Excluye la carpeta de tests del linting y validación de tipos).

### 3. Frontend (React + Vite)

1. Ingresa al directorio del frontend:
   ```bash
   cd frontend
   ```
2. Instala las dependencias:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```

**Comandos adicionales del Frontend:**
- **Linter:** `npm run lint`

---

## 📖 Diseño del Motor de Batalla: Desglose Analítico del Turno

El flujo de batalla está diseñado para ser determinista en el servidor. A continuación se detalla cómo el motor procesa el turno una vez que se han recolectado todas las acciones:

### 1. Fase de Selección
1. El motor espera la instrucción de ambos lados antes de avanzar.
2. Las acciones válidas son `move` y `switch`.
3. La resolución del turno solo empieza cuando ya existen todas las decisiones requeridas para los Pokémon activos.

### 2. Fase de Cambio (Switch)
1. Si existe una orden de `switch`, esta fase toma prioridad absoluta sobre los movimientos del turno.
2. Primero se declara la retirada del Pokémon activo. (En 5ta Generación, aquí el contador de turnos de `sleep` se reinicia a cero).
3. Si el cambio se concreta, se marca `isRevealed = true`, se actualiza `activePokemonInstanceIds`.

### 3. Determinación del Orden de Acción
1. Las acciones de `move` pendientes se ordenan primero por la **prioridad base** del movimiento.
2. Dentro del mismo grupo de prioridad, el desempate se hace por **Velocidad efectiva** actual (incluyendo modificadores como la reducción por parálisis).
3. Si la Velocidad exacta es idéntica, el motor resuelve un `speed tie` aleatorio al 50%.

### 4. Ciclo de Ejecución de Movimientos
1. Antes de ejecutar la acción, se verifica si el usuario sigue con PS > 0. Si fue debilitado antes de actuar, su acción se descarta.
2. Se validan impedimentos de estado: `freeze`, `sleep`, `flinch`, `paralysis` y `confusion`. Si un estado consume el turno o la `confusion` hace que el usuario se golpee a sí mismo, el movimiento se cancela.
3. Se resuelve la precisión (`accuracy`) comparándola contra los modificadores de precisión y evasión.
4. Si el movimiento impacta, se calcula el daño base aplicando `STAB`, efectividad de tipos, críticos y modificadores estadísticos.
5. Tras el daño, se resuelven efectos secundarios inmediatos (cambios de stages, `recoil`, drenado, alteraciones de estado).
6. Si un usuario cae por `recoil`, se debilita en el instante y el efecto repercute en la cola de acciones restante.

### 5. Fase de Resolución Residual
1. Al vaciarse la cola de movimientos, se aplican los efectos de clima (`sandstorm`, `hail`) para los Pokémon no inmunes.
2. Se resuelve `Leech Seed` (drenando 1/8 de los PS máximos y curando al agresor).
3. Se aplica el daño residual de estados (`burn`, `poison`, `toxic`), respetando la progresión exponencial de `toxic`.
4. Se verifican los debilitamientos finales, actualizando el estado de combate (`currentHp`, `status`, `fainted`, etc.).
5. Se exige la elección de reemplazos a los entrenadores si quedaron espacios vacíos y aún tienen Pokémon en reserva.
6. Finalmente, se genera un nuevo **snapshot de batalla** y la lista de acciones efectivamente ejecutadas para iniciar el siguiente ciclo.
