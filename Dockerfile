FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY kernel ./kernel
COPY api ./api
COPY sdk ./sdk
COPY adapters ./adapters
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY docker-entrypoint.sh ./docker-entrypoint.sh

RUN pip install --no-cache-dir . \
    && chmod +x ./docker-entrypoint.sh

EXPOSE 8000

# python:3.13-slim has no curl; urllib avoids adding an OS package just for
# this check. A non-2xx/timeout exit code marks the container unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/healthz', timeout=3)" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]

