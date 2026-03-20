# syntax=docker/dockerfile:1

## Build stage: install Python dependencies with uv (fast, cached)
FROM python:3.13-slim AS builder

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r /code/requirements.txt

## Runtime stage: clean image with no build tools
FROM python:3.13-slim AS runtime

WORKDIR /code

ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder (no uv/pip in final image)
COPY --from=builder /usr/local /usr/local

COPY . /code/
RUN chmod +x /code/start-web.sh

RUN ON_VPS=TRUE SECRET_KEY=build-placeholder DATABASE_URL=sqlite://:memory: \
    python manage.py collectstatic --noinput

RUN groupadd -r app && useradd -r -g app -d /code -s /sbin/nologin app && \
    chown -R app:app /code
USER app

EXPOSE 8000

CMD ["/code/start-web.sh"]
