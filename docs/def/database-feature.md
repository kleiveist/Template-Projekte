<!-- AUTO-GENERATED:backlink START -->
[← Back](def.md)
<!-- AUTO-GENERATED:backlink END -->
# Database feature

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-06 |
| Audience | Backend developers and operators |
| Related ATP | N/A — template-level optional capability |

## Purpose

This document defines the optional SQL database capability. PostgreSQL is an optional capability of backend-enabled projects, not a project profile and not a mandatory template dependency.

## Scope

### Included

- SQLAlchemy 2.x engine and session infrastructure;
- a model-free declarative base;
- Alembic migration infrastructure;
- PostgreSQL support through Psycopg 3;
- database diagnostics and explicit migration commands; and
- unit and optional PostgreSQL integration tests.

### Excluded

- business models and repositories;
- automatic schema creation or migration during application startup;
- Docker, deployment, backup, replication, and high availability; and
- authentication or authorization.

## Feature architecture

```mermaid
flowchart TD
    Profile[Backend-enabled platform profile]
    Postgres[postgres capability]
    Database[database capability]
    Backend[backend feature]
    Project[Generated project]

    Postgres -->|requires| Database
    Database -->|requires| Backend
    Profile --> Project
    Postgres --> Project
```

`database` owns generic SQLAlchemy and Alembic infrastructure. `postgres` owns the Psycopg driver, the PostgreSQL URL example, and PostgreSQL integration tests. This separation permits a later database provider, such as SQLite, to reuse `database` without depending on Psycopg.

Generate a PostgreSQL-capable project with:

```sh
python tools/control.py init --profile web-cloud --with postgres
```

The generator resolves `database` transitively. It rejects profiles without `backend` instead of silently changing their platform architecture.

## Runtime architecture

```mermaid
flowchart LR
    Client[Browser or Tauri client]
    API[FastAPI backend]
    Session[SQLAlchemy session]
    Engine[SQLAlchemy engine]
    PostgreSQL[(PostgreSQL)]

    Client -->|HTTPS| API
    API --> Session
    Session --> Engine
    Engine -->|Psycopg 3| PostgreSQL
```

Frontend and Tauri code never receives `DATABASE_URL` and never connects to PostgreSQL directly.

## Configuration

| Name | Default | Allowed value | Security impact |
| --- | --- | --- | --- |
| `DATABASE_URL` | None | Valid server-side SQLAlchemy URL; PostgreSQL projects use `postgresql+psycopg` | May contain credentials; never expose it through `VITE_` variables or commit production values |
| `DATABASE_URL_TEST` | None | URL of an isolated PostgreSQL test database | Used only by the optional integration test; never point it at production |

A generated PostgreSQL project adds this safe placeholder to `.env.example`:

```env
DATABASE_URL=postgresql+psycopg://app:change-me@127.0.0.1:5432/app
```

Backend Settings read `DATABASE_URL` from the process environment or root `.env`, with the process environment taking priority. The value uses Pydantic `SecretStr`; database configuration unwraps it only when creating an engine. Tooling uses the same environment contract and masks credentials in output.

## SQLAlchemy baseline

`backend/app/db/base.py` defines the empty declarative `Base`. Derived projects add their own models and import them before Alembic autogeneration.

`backend/app/db/engine.py` creates engines lazily. Importing the FastAPI application does not open a database connection. `backend/app/db/session.py` creates SQLAlchemy 2.x session factories and exposes `get_db_session()` as a FastAPI-compatible generator dependency that closes every session.

The template never calls `create_all()` or `drop_all()`.

## Migration workflow

Set `DATABASE_URL` in the process environment, then use explicit commands:

```sh
python tools/control.py db doctor
python tools/control.py db doctor --connect
python tools/control.py db upgrade
python tools/control.py db downgrade
python tools/control.py db revision --message "add example"
```

`db doctor` is read-only. The connection probe runs only with `--connect` and executes `SELECT 1`. Migration commands delegate to Alembic. FastAPI startup never invokes Alembic automatically.

No initial migration exists because the template contains no business models.

## Tests

Generic unit tests use an in-memory SQLite engine and require no PostgreSQL service:

```sh
python tools/control.py test --suite database
```

The PostgreSQL suite runs only when `DATABASE_URL_TEST` is configured and reachable. Otherwise Pytest reports a skip:

```sh
python tools/control.py test --suite postgres
```

## Verification

```sh
python tools/control.py init --profile web-cloud --with postgres --dry-run
python tools/control.py db doctor
python tools/control.py test --suite database
python tools/control.py test --suite postgres
```

## Related documents

- [Framework architecture](architecture.md)
- [Project profiles](project-profiles.md)
- [Runtime configuration](configuration.md)
- [Tooling Guide](../tools/tooling.md)
- [Documentation Standard](../README.md)
