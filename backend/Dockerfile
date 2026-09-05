# Build context is the REPO ROOT (see docker-compose.yml: `context: .`,
# `dockerfile: backend/Dockerfile`), not ./backend. The scraper/ package is
# a sibling of backend/, not a subdirectory of it -- building with
# `context: ./backend` (the previous setup) silently excluded scraper/ from
# the image entirely, so any code importing `scraper.*` at runtime would
# have failed with ModuleNotFoundError inside the container even though it
# worked fine locally.

FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies first (better layer caching: this layer only
# invalidates when requirements.txt changes, not on every code change).
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Now bring in both packages the running app actually needs.
COPY backend/ ./backend/
COPY scraper/ ./scraper/

# `app.*` lives under backend/, `scraper.*` lives at the repo root -- both
# need to be importable, so both are on the path. uvicorn's --app-dir
# handles the `app` import; PYTHONPATH covers `scraper`.
ENV PYTHONPATH=/app

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"]

# No --reload here on purpose -- this is the production-safe default.
# Local dev overrides this via `command:` in docker-compose.yml instead of
# baking a dev-only flag into the image itself.
CMD ["uvicorn", "app.main:app", "--app-dir", "/app/backend", "--host", "0.0.0.0", "--port", "8000"]
