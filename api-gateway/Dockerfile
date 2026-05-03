FROM python:3.11-slim

WORKDIR /app

COPY api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY api-gateway/app/ ./app/

EXPOSE 8000

# Use PORT env var (Render sets this), fallback to 8000 for local Docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
