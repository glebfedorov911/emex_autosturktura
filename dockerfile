# Используем официальный Python образ в качестве базового
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду для запуска приложения
# CMD ["sh", "-c", "alembic upgrade head && playwright install-deps && playwright install && python main.py"]
CMD ["sh", "-c", "alembic upgrade head && python main.py"]

# Открываем порт для доступа
EXPOSE 8000