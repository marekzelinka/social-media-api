# Social Media REST API

This project presents an REST API for a social media application, with support for user auth, CRUD actions for posts and voting mechanizm. It's coded using **FastAPI**, **SQLModel** for database ORM and data validation, **alembic** for database migration, and **PostgreSQL** via **Neon**.

## Prerequisites

- This project uses the modern `pyproject.toml` standard for dependency management and requires the `uv` tool to manage the environment:
  - **Ensure `uv` is installed** globally on your system. If not, follow the official installation guide for [`uv`](https://docs.astral.sh/uv/).

- A [Neon account](https://console.neon.tech/signup) for serverless Postgres.


## Setup

1.  **Install project dependencies**

    ```sh
    uv sync
    ```

2.  **Setup env variables**

    ```sh
    cp .env.example .env
    ```


3.  **Start app in dev mode**

    ```sh
    uv run uvicorn app.main:app --reload
    # or
    just dev
    ```

4.  **Visit OpenAPI docs in browser**

    ```sh
    open http://localhost:8000/docs
    ```

## Development

1. Setup your editor to work with [ruff](https://docs.astral.sh/ruff/editors/setup/) and [ty](https://docs.astral.sh/ty/editors/), this way you get formating on save and proper type checking.

2. Setup [just](https://just.systems/man/en/introduction.html) to run project-specific commands, and also the [justfile extension](https://just.systems/man/en/editor-support.html) for your editor, and use the provided [`justfile`](./justfile) to run commands.

## Tech Stack

- `FastAPI` : A Web / API framework
- `SQLModel` : A library for interacting with SQL databases and data validation
- `Uvicorn` : An ASGI server for our app
- `PyTest` : Test runner
