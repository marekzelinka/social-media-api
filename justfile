start:
    uv run uvicorn app.main:app

dev:
    uv run uvicorn app.main:app --reload

test:
    uv run pytest

typecheck:
    uv run ty check

lint:
    uv run ruff check --fix

format:
    uv run ruff format
