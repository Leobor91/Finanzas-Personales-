FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8000

# Use a fixed port inside container; Render uses $PORT but for Docker we bind 8000
ENV PORT=8000

CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
