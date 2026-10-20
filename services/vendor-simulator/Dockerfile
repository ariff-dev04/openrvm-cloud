FROM python:3.12-slim

WORKDIR /app

# Install FastAPI, Uvicorn, and HTTPX for async webhook pushing
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

# Create a non-root user for container security (DevOps Best Practice)
RUN useradd -m -u 1001 appuser
USER appuser

COPY main.py .

EXPOSE 8081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
