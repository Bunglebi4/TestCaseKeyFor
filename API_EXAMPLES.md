# API Examples

## Создание пользователя

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: test-trace-123" \
  -d '{
    "name": "Иван",
    "surname": "Иванов",
    "password": "secret123"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Иван",
  "surname": "Иванов",
  "created_at": "2024-12-04T10:30:00.123Z",
  "updated_at": "2024-12-04T10:30:00.123Z"
}
```

Headers:
```
X-Trace-Id: test-trace-123
```

## Получение списка пользователей

```bash
curl "http://127.0.0.1:8000/users/?limit=10&offset=0"
```

Response:
```json
[
  {
    "id": 1,
    "name": "Иван",
    "surname": "Иванов",
    "created_at": "2024-12-04T10:30:00.123Z",
    "updated_at": "2024-12-04T10:30:00.123Z"
  }
]
```

## Получение пользователя по ID

```bash
curl "http://127.0.0.1:8000/users/1"
```

Response:
```json
{
  "id": 1,
  "name": "Иван",
  "surname": "Иванов",
  "created_at": "2024-12-04T10:30:00.123Z",
  "updated_at": "2024-12-04T10:30:00.123Z"
}
```

## Обновление пользователя

```bash
curl -X PUT "http://127.0.0.1:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Петр",
    "surname": "Петров"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Петр",
  "surname": "Петров",
  "created_at": "2024-12-04T10:30:00.123Z",
  "updated_at": "2024-12-04T10:32:00.456Z"
}
```

## Частичное обновление (только имя)

```bash
curl -X PUT "http://127.0.0.1:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Алексей"
  }'
```

## Удаление пользователя

```bash
curl -X DELETE "http://127.0.0.1:8000/users/1"
```

Response: 204 No Content

## Пример с trace_id

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: custom-trace-id-12345" \
  -v \
  -d '{
    "name": "Мария",
    "surname": "Сидорова",
    "password": "pass456"
  }'
```

В ответе будет заголовок:
```
< X-Trace-Id: custom-trace-id-12345
```

И в логах будет:
```json
{
  "event": "Request started",
  "trace_id": "custom-trace-id-12345",
  "method": "POST",
  "path": "/users/"
}
```

## Проверка событий в RabbitMQ

1. Откройте RabbitMQ Management UI: http://localhost:15672
2. Логин/Пароль: guest/guest
3. Перейдите в раздел "Queues"
4. Найдите очередь "user_events_queue"
5. Посмотрите сообщения

Или проверьте логи приложения, где Consumer будет логировать полученные события:
```json
{
  "event": "Event received",
  "trace_id": "custom-trace-id-12345",
  "event_type": "user.created",
  "user_id": 1,
  "timestamp": "2024-12-04T10:30:00.123Z"
}
```
