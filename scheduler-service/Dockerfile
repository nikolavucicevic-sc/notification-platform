FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "1"]
