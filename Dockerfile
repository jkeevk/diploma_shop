FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    python3-dev \
    netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ./nginx/ssl/localhost.crt /etc/nginx/ssl/localhost.crt
COPY ./nginx/ssl/localhost.key /etc/nginx/ssl/localhost.key

CMD ["gunicorn", "orders.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]