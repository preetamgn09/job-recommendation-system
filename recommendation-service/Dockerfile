FROM python:3.11-slim

WORKDIR /app

COPY recommendation-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY recommendation-service/app/ ./app/

EXPOSE 8003

# Use PORT env var (Render sets this), fallback to 8003 for local Docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}
