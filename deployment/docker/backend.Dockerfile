# syntax=docker/dockerfile:1.7
FROM python:3.14.7-slim-bookworm AS dependencies

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv

RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /build
COPY backend/requirements*production.* ./backend/
RUN pip install --no-cache-dir --require-hashes --requirement backend/requirements-production.lock \
    && if [ -f backend/requirements-database-production.lock ]; then pip install --no-cache-dir --require-hashes --requirement backend/requirements-database-production.lock; fi \
    && if [ -f backend/requirements-postgres-production.lock ]; then pip install --no-cache-dir --require-hashes --requirement backend/requirements-postgres-production.lock; fi

FROM python:3.14.7-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --from=dependencies /opt/venv /opt/venv
WORKDIR /app
COPY --chown=app:app VERSION project-profile.toml ./
COPY --chown=app:app config ./config
COPY --chown=app:app profiles ./profiles
COPY --chown=app:app tools ./tools
COPY --chown=app:app backend ./backend

USER 10001:10001
WORKDIR /app/backend
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
