# YES, BOSS! Backend

This directory contains the Python backend skeleton for the game.

## Layout

- `app/`: FastAPI application, settings, API, and future domain/service modules
- `tests/`: pytest suite and fixtures
- `docs/`: integration notes and blacklist data

## Verify

Run these from `backend/`:

```bash
pytest -q
ruff check app tests
mypy app
```

Do not run `uvicorn`. Wait for task 21.
