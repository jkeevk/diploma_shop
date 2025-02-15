FROM python:3.12-alpine

COPY .env .env

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000