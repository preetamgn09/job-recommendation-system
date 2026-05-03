FROM python:3.11-slim

WORKDIR /app

COPY job-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY job-service/app/ ./app/

EXPOSE 8002

# Use PORT env var (Render sets this), fallback to 8002 for local Docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8002}
