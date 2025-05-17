# Используем официальный Python образ в качестве базового
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Создаем виртуальное окружение
RUN python3 -m venv venv

# Активируем виртуальное окружение и обновляем pip
RUN . venv/bin/activate && pip install --upgrade pip

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

RUN alembic revision -m "create accounts table"
RUN alembic revision --autogenerate -m "Create products table"
# Указываем команду для запуска приложения
CMD ["sh", "-c", "alembic upgrade head && playwright install-deps && playwright install && python main.py"]
# CMD ["sh", "-c", "alembic upgrade head && python main.py"]

# Открываем порт для доступа
EXPOSE 8000