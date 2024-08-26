# Используем официальный Python образ в качестве базового
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN mkdir /tmp/testpsycopg2
RUN cd /tmp/testpsycopg2
RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install wheel
RUN apt-get install libpq-dev
RUN apt-get install python3-dev
RUN apt-get install build-essential
RUN cd /app
RUN . venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду для запуска приложения
CMD ["sh", "-c", "alembic upgrade head && playwright install-deps && playwright install && python main.py"]
# CMD ["sh", "-c", "alembic upgrade head && python main.py"]

# Открываем порт для доступа
EXPOSE 8000