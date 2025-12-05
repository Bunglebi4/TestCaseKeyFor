# User Management API

REST API для управления пользователями на базе LiteStar, PostgreSQL и RabbitMQ.

## Требования

- Python 3.12+
- PostgreSQL 16+
- RabbitMQ 3+
- Poetry 1.8.3+

## Установка и запуск
### 0. можно запустить ./setup.sh(у меня работает с: )

### 1. Клонирование репозитория 

```bash
git clone git@github.com:Bunglebi4/TestCaseKeyFor.git
cd user-management-api
```

### 2. Установка зависимостей

```bash
poetry install
```

### 3. Запуск инфраструктуры (PostgreSQL + RabbitMQ)

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL на порту 5432
- RabbitMQ на порту 5672 (управление: http://localhost:15672, guest/guest)

### 4. Настройка окружения

```bash
cp .env.example .env
```

Содержимое `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/userdb
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
LOG_LEVEL=INFO
```

### 5. Создание миграций и применение

```bash
poetry run alembic revision --autogenerate -m "Initial migration"
poetry run alembic upgrade head
```

### 6. Запуск приложения

```bash
poetry run litestar run --host 127.0.0.1 --port 8000 --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

Swagger документация: http://127.0.0.1:8000/docs

## Использование API

### Создание пользователя

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван",
    "surname": "Иванов",
    "password": "secret123"
  }'
```

### Получение списка пользователей

```bash
curl "http://127.0.0.1:8000/users/"
```

### Получение пользователя по ID

```bash
curl "http://127.0.0.1:8000/users/1"
```

### Обновление пользователя

```bash
curl -X PUT "http://127.0.0.1:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Петр",
    "surname": "Петров"
  }'
```

### Удаление пользователя

```bash
curl -X DELETE "http://127.0.0.1:8000/users/1"
```

## Логирование и trace_id

Каждый запрос получает уникальный `trace_id`:
- Читается из заголовка `X-Request-Id` (если присутствует)
- Генерируется автоматически (UUID)
- Присутствует во всех логах
- Возвращается клиенту в заголовке `X-Trace-Id`

Пример лога:
```json
{
  "event": "Request started",
  "level": "info",
  "timestamp": "2024-12-04T10:30:00.123Z",
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/users/"
}
```

## RabbitMQ Events

При создании, обновлении или удалении пользователя автоматически публикуются события:
- `user.created`
- `user.updated`
- `user.deleted`

Consumer автоматически обрабатывает эти события и логирует их с сохранением `trace_id`.

Структура события:
```json
{
  "event_type": "user.created",
  "user_id": 1,
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2024-12-04T10:30:00.123Z",
  "data": {
    "name": "Иван",
    "surname": "Иванов"
  }
}
```

## Структура базы данных

Таблица `users`:

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT | Primary key (автоинкремент) |
| name | TEXT | Имя |
| surname | TEXT | Фамилия |
| password | TEXT | Пароль |
| created_at | TIMESTAMP | Дата создания (UTC) |
| updated_at | TIMESTAMP | Дата обновления (UTC) |

## Технологический стек

- **Framework**: LiteStar 2.x
- **Database**: PostgreSQL 16 + Advanced SQLAlchemy
- **Message Queue**: RabbitMQ + aio-pika + faststream
- **Logging**: structlog
- **Validation**: msgspec
- **Package Manager**: Poetry 1.8.3

## Тестирование

## Особенности реализации

### Middleware для trace_id
- Автоматически перехватывает все HTTP запросы
- Генерирует/читает trace_id
- Добавляет в контекст логгера
- Логирует начало, завершение и ошибки запроса

### Repository Pattern
- Изолирует логику доступа к данным
- Упрощает тестирование
- Позволяет легко менять источник данных

### Service Layer
- Содержит всю бизнес-логику
- Координирует работу репозиториев
- Публикует события в RabbitMQ

### Event-Driven подход
- Producer публикует события при изменениях
- Consumer обрабатывает события асинхронно
- trace_id передаётся через очередь


### Потрачено 3,5 часа