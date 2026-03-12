FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH=/app
# Ensure Python outputs are not buffered
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-u", "-m", "app.main"]
