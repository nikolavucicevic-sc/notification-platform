FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY create_admin.py .
COPY alembic ./alembic
COPY alembic.ini .

# Ensure Python outputs are not buffered
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8002

# Startup: run migrations, create admin, then start the server
RUN echo '#!/bin/bash\nalembic upgrade head\npython create_admin.py || true\nexec uvicorn app.main:app --host 0.0.0.0 --port 8002' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
