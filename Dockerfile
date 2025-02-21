FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install uvicorn

COPY . /app/

CMD ["uvicorn", "orders.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
