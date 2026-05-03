FROM python:3.11-slim

WORKDIR /app

COPY event-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY event-service/app/ ./app/

CMD ["python", "-m", "app.main"]
