# Pastebin
A FastAPI service for code sharing.

![tests](https://github.com/sparrowsurya/pastebin-api/actions/workflows/tests.yaml/badge.svg)


## Prerequisites
- [uv](https://github.com/astral-sh/uv) (fast Python package installer and resolver)
- Python 3.12 (managed automatically by `uv`)

## Setup & Running

### 1. Clone the repository
```sh
git clone https://github.com/sparrowsurya/pastebin-api
```

### 2. Environment Configuration (Optional)
The project comes pre-configured with default settings using a local SQLite database (`sqlite:///./db.sqlite3`), so creating a `.env` file is optional for local development and testing.

To override settings (e.g. for PostgreSQL in production), create a `.env` file:
```env
ENV_NAME=development
BASE_URL=127.0.0.1:8000
DB_URL=postgresql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE
INTERVAL=3600
```

### 3. Sync dependencies
Installs the locked dependencies into a local virtual environment:
```sh
uv sync
```

### 4. Run the API
Start the application using `uvicorn`:
```sh
uv run uvicorn api.main:app --log-config=log_config.json
```

---

## Running Tests
Run the test suite via the builtin `unittest` framework:
```sh
uv run python -m unittest discover
```