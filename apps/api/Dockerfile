FROM python:3.11-slim

WORKDIR /app

# Install build tools if needed
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY apps/api/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install ollama

# Copy the rest of the application code
COPY . /app/

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]