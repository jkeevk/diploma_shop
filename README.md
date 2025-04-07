[![Python](https://img.shields.io/badge/python-3.12.8-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1.7-green?logo=django)](https://www.djangoproject.com/)
[![PyPI Version](https://img.shields.io/pypi/v/djangorestframework.svg)](https://pypi.org/project/djangorestframework/)
[![Tests](https://img.shields.io/github/actions/workflow/status/jkeevk/diploma_shop/coverage.yml?branch=main&label=tests&logo=github)](https://github.com/jkeevk/diploma_shop/actions/workflows/coverage.yml)
[![Coverage Status](https://coveralls.io/repos/github/jkeevk/diploma_shop/badge.svg)](https://coveralls.io/github/jkeevk/diploma_shop)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Last Commit](https://img.shields.io/github/last-commit/jkeevk/diploma_shop.svg)](https://github.com/your-username/your-repo/commits)
[![Open Issues](https://img.shields.io/github/issues-raw/jkeevk/diploma_shop.svg)](https://github.com/your-username/your-repo/issues)
[![License](https://img.shields.io/github/license/jkeevk/diploma_shop)](https://github.com/jkeevk/diploma_shop/blob/main/LICENSE)
# Дипломный проект: Backend-приложение для автоматизации закупок

## Описание проекта

Данный проект представляет собой backend-приложение для автоматизации закупок в розничной сети. Приложение разработано на Django Rest Framework и предоставляет REST API для взаимодействия с сервисом. Основная цель проекта — автоматизация процессов заказа товаров, управление заказами, импорт и экспорт товаров, а также интеграция с email-уведомлениями.

## Цель проекта

Разработка backend-части сервиса заказа товаров для розничных сетей, включая:
- Проработку моделей данных с использованием Django ORM.
- Реализацию импорта и экспорта товаров.
- Внедрение системы управления заказами.
- Интеграцию с email-уведомлениями для подтверждения заказов и уведомлений поставщиков.

## Основные функции

### Для клиентов (покупателей):
- Регистрация, авторизация и восстановление пароля через API.
- Просмотр каталога товаров от нескольких поставщиков.
- Формирование заказов с товарами от разных поставщиков.
- Получение подтверждения заказа по email.
- Просмотр истории заказов и их статусов.

### Для поставщиков:
- Обновление прайс-листов через API.
- Управление приёмом заказов (включение/отключение).
- Получение списка заказов с товарами из их прайс-листов.
- Получение уведомления о поступившем заказе по email.
- Возможность обновления статусов заказов (например, "Новый", "Отправлен", "Доставлен").

### Для администраторов:
- Управление пользователями (клиентами и поставщиками).
- Мониторинг заказов и их статусов.
- Импорт и экспорт данных о товарах.
- Настройка параметров системы.
- Полный контроль через админку.
- Запуск тестов и проверка покрытия кода тестами.

## Технологии

- **Python 3.10+**  
- **Django** — веб-фреймворк для создания приложения  
- **Django Rest Framework (DRF)** — создание RESTful API  
- **PostgreSQL** — основная база данных  
- **Redis** — кеширование и работа с Celery  
- **Celery** — выполнение асинхронных задач, таких как отправка email-уведомлений, запуск тестов, импорт/экспорт товаров  
- **Docker** — контейнеризация приложения и зависимостей  
- **Nginx** — reverse proxy для обработки HTTP-запросов  
- **Swagger/Redoc** — автоматическая документация API  
- **pytest**, **pytest-django**, **pytest-cov** — написание, запуск unit- и integration-тестов, проверка покрытия кода тестами
- **Sentry** — мониторинг и отслеживание ошибок приложения
- **Silk** - мониторинг и отслеживание перегруженных запросов к БД
- **GitHub Actions** - автоматизации CI/CD процессов, включая запуск тестов и выгрузку результатов в Coveralls


## Установка и запуск

### Предварительные требования

1. Установить [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/install/).
2. Убедиться, что у вас установлена ОС Linux или MacOS. (опционально)
3. Установить Python 3.10 или новее. (опционально)
4. Установить IDE с поддержкой Python (например, PyCharm, VS Code). (опционально)

### Порядок запуска

1. Клонировать репозиторий:
   
   ```bash
   git clone https://github.com/jkeevk/diploma_shop.git
   cd diploma_shop
   ```

2. Заполнить файл `.env` необходимыми значениями переменных окружения.

3. Запустить контейнеры с помощью Docker Compose:

    ```bash
    docker-compose up -d --build
    ```

Во время запуска будут выполнены миграции базы данных, создан суперпользователь с почтой `admin@admin.com` и паролем `admin`, собраны статические файлы, и будут развернуты контейнеры Django, PostgreSQL, Celery, Redis, Nginx и Tests.

После успешного запуска сервер будет доступен по адресу: [https://localhost/](https://localhost/)

### Тестирование

При запуске контейнеров тесты запустятся автоматически.
Проверка результатов командой:

```bash
docker-compose tests logs
```

Запуск тестов вручную:

```bash
docker-compose exec app pytest
```

Покрытие кода тестами:

[![Coverage Status](https://coveralls.io/repos/github/jkeevk/diploma_shop/badge.svg?branch=main)](https://coveralls.io/github/jkeevk/diploma_shop?branch=main)

### CI/CD с GitHub Actions

Для автоматизации процессов CI/CD в проекте настроены GitHub Actions. При каждом пуше изменений в репозиторий автоматически запускаются тесты, а результаты покрытия кода выгружаются в Coveralls. Это позволяет поддерживать высокое качество кода и быстро выявлять возможные проблемы.

### Документация API

Документация API доступна в следующих форматах:

- Swagger: [https://localhost/api/docs/swagger](https://localhost/api/docs/swagger)
- Redoc: [https://localhost/api/docs/redoc](https://localhost/api/docs/redoc)

Примеры и формат данных для обновления прайса поставщиков находятся в папке `data/`.

### Контакты

Если у вас есть вопросы или предложения, свяжитесь со мной:

- Email: jkeevk@yandex.ru
- TG: [jkeeincredible](https://t.me/jkeeincredible)
- GitHub: [jkeevk](https://github.com/jkeevk/)

Ссылка на задание дипломного проекта: [Диплом](https://github.com/netology-code/python-final-diplom)
