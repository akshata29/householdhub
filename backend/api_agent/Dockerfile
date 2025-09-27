FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy common files
COPY common/ ./common/
COPY a2a/ ./a2a/
COPY requirements.txt .

# Copy service-specific files
COPY api_agent/ ./api_agent/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]