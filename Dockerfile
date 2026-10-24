FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DRY_RUN=true
ENV SPEND_CAP_SOL=0.02

ENTRYPOINT ["python3", "-m", "src.telemetry_collector"]
CMD ["--data-dir", "./data"]
