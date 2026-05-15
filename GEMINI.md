# Puchamon - Agent Instructions

## Project Structure
- `backend/`: Python 3.12 FastAPI (main active development)
- `frontend/`: React + Vite + TypeScript (placeholder)
- `docs/`: Documentation

## Backend Development

### Required Setup
```bash
cd backend
uv sync
```
Create `.env` with: `DATABASE_URI`, `DATABASE_NAME`

### Commands
- **Run server**: `uv run start` (starts on http://localhost:8000)
- **Run tests**: `uv run pytest`
- **Lint**: `uv run ruff check .`

### Test Configuration
- Uses pytest with `asyncio_mode = "auto"` (configured in pyproject.toml)
- Test files go in `tests/`

### Code Style
- Ruff configured in `pyproject.toml`: line-length 150, Google docstrings
- Excludes tests from linting and type checking

## Frontend Development
```bash
cd frontend
npm install
npm run dev
npm run lint
```

## Important Context
- Battle system is authoritative server-side
- Supports 1v1, 2v2, 3v3 battles with player-vs-AI and AI-vs-AI modes
- `ability` and `item` exist in data model but have no functional effect yet
- MongoDB used for data persistence (requires `mongosh` to load initial Pokemon data)