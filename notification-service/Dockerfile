FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libpq-dev curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

ENV PYTHONUNBUFFERED=1

EXPOSE 8002

RUN printf '#!/bin/sh\nset -e\necho "[start.sh] Running Alembic migrations..."\nalembic upgrade head\necho "[start.sh] Migrations complete"\nexec uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 1\n' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]
