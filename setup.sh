#!/bin/bash

echo "Starting User Management API..."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED} $1 не установлен${NC}"
        echo "Установите $1: $2"
        exit 1
    else
        echo -e "${GREEN} $1 установлен${NC}"
    fi
}

echo "📋 Проверка требований..."
check_command "docker" "https://docs.docker.com/get-docker/"
check_command "docker-compose" "https://docs.docker.com/compose/install/"
check_command "poetry" "curl -sSL https://install.python-poetry.org | python3 -"
echo ""

echo "🐍 Проверка Python..."
if command -v python3.12 &> /dev/null; then
    echo -e "${GREEN} Python 3.12 найден${NC}"
else
    echo -e "${YELLOW}  Python 3.12 не найден, poetry попробует использовать доступную версию${NC}"
fi
echo ""

echo "📦 Установка зависимостей..."
poetry install

if ! poetry run python -c "import sniffio" 2>/dev/null; then
    echo -e "${YELLOW} Добавление недостающих зависимостей...${NC}"
    poetry add sniffio pydantic-settings
fi
echo ""

# Запуск Docker
echo "🐳 Запуск PostgreSQL и RabbitMQ..."
docker-compose up -d
echo ""

# Ожидание готовности PostgreSQL
echo "⏳ Ожидание готовности PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN} PostgreSQL готов${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED} PostgreSQL не запустился за 30 секунд${NC}"
        echo "Проверьте логи: docker-compose logs postgres"
        exit 1
    fi
    echo "Попытка $i/30..."
    sleep 1
done
echo ""

# Ожидание готовности RabbitMQ
echo "⏳ Ожидание готовности RabbitMQ..."
for i in {1..30}; do
    if curl -s http://localhost:15672 &> /dev/null; then
        echo -e "${GREEN} RabbitMQ готов${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  RabbitMQ не запустился за 30 секунд (приложение продолжит работу)${NC}"
        break
    fi
    echo "Попытка $i/30..."
    sleep 1
done
echo ""

echo "Проверка базы данных..."
docker-compose exec -T postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw userdb
if [ $? -ne 0 ]; then
    echo "Создание базы данных userdb..."
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE userdb;"
fi
echo -e "${GREEN} База данных userdb готова${NC}"
echo ""

echo "Применение миграций..."
poetry run alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN} Миграции применены${NC}"
else
    echo -e "${YELLOW}  Ошибка при применении миграций (возможно уже применены)${NC}"
fi
echo ""

echo "🔍 Финальная проверка..."
echo "PostgreSQL: http://localhost:5432 (postgres/postgres)"
echo "RabbitMQ UI: http://localhost:15672 (guest/guest)"
echo ""

echo -e "${GREEN}✅ Установка завершена!${NC}"
echo ""
echo "Для запуска приложения выполните:"
echo -e "${YELLOW}poetry run litestar run --host 127.0.0.1 --port 8000 --reload${NC}"
echo ""
echo "Swagger UI будет доступен по адресу:"
echo -e "${YELLOW}http://127.0.0.1:8000/docs${NC}"
echo ""
