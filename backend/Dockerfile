FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .
COPY simulate_scans.py .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI and the WebSockets
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
