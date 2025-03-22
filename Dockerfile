FROM python:3.12

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install uvicorn

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
COPY . /app/

COPY ./nginx/ssl/localhost.crt /etc/nginx/ssl/localhost.crt
COPY ./nginx/ssl/localhost.key /etc/nginx/ssl/localhost.key

CMD ["uvicorn", "orders.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
