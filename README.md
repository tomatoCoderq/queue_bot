# Queue Bot

> Task and group management with FastAPI + Telegram bot.

## About

Simple Backend API (FastAPI) + Telegram bot (Aiogram) for managing students, groups and tasks. Operators can view profiles, assign tasks, manage groups, and update/delete users.

### Features

- ✅ Students, tasks and groups management
- 🧑‍🏫 Operator flows: assign tasks, update user data, remove from groups
- 🗓 Notifications and scheduler for tasks

### Technologies

- Python 3.11+ & uv (not optional, use it!!!)
- FastAPI, Aiogram, aiogram-dialog
- SQLModel, SQLAlchemy, Alembic
- Docker & Docker Compose

## Development

### Set up for development

1. Install Python 3.11+ (and [uv](https://docs.astral.sh/uv/))
2. Install dependencies:
	```bash
	# recommended
	uv sync
	# or with pip
	python -m venv .venv
	source .venv/bin/activate
	pip install -e .
	```
3. Create environment file `.env` in repository root as per `.env.example
4. Apply database migrations (SQLite by default):
	```bash
	alembic upgrade head
	```
5. Start API locally:
	```bash
	uv run -m src.api
	```
6. Start Telegram bot:
	```bash
	python -m bot
	```

## Using Docker
1. Ensure Docker and Docker Compose are installed.
2. Create `.env` file in the project root based on `.env.example`.
3. Build and start services:
    ```bash
    docker-compose up --build
    ```

4. The API will be accessible at `http://localhost:8000` and the bot will connect automatically.

### Troubleshooting

- Bot cannot reach API: ensure API is up, `API_HOST`/`API_PORT` correct. In Docker use service name (`api`) instead of `localhost`.
- Alembic errors: verify DSN in `alembic.ini` matches your DB (SQLite/Postgres).
- Invalid token: confirm `TOKEN` is correct and bot can send messages.

## Project structure

- `src/api/app.py` — FastAPI application entrypoint
- `bot/__main__.py` — Telegram bot entrypoint
- `src/modules/*` — API modules (users, tasks, groups, files)
- `bot/modules/*` — bot dialogs, handlers, services
- `alembic/` — migration scripts
