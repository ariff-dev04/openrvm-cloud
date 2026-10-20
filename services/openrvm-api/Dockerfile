FROM python:3.12-slim

WORKDIR /app

# Install FastAPI, PostgreSQL driver (psycopg2-binary), SQLAlchemy, Redis, and HTTPX
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary redis httpx pydantic

# Run as non-root user (UID 1001)
RUN useradd -m -u 1001 appuser
USER appuser

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
