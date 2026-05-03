FROM python:3.11-slim

WORKDIR /app

COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY user-service/app/ ./app/

EXPOSE 8001

# Use PORT env var (Render sets this), fallback to 8001 for local Docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}
