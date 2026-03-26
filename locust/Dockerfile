FROM python:3.11-slim

WORKDIR /app

# Install locust
RUN pip install locust==2.20.0

# Copy locustfile
COPY locustfile.py /app/

# Expose Locust web UI port
EXPOSE 8089

# Default command
CMD ["locust", "-f", "locustfile.py", "--host=http://notification-service:8002"]
