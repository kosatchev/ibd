# Использование официального образа Python 3.11 с минимальной версией (slim)
FROM python:3.11-slim

# Установка рабочей директории для приложения
WORKDIR /app

# Установка системных зависимостей, необходимых для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \  # Установка компилятора GCC, необходимого для компиляции psycopg2
    libpq-dev \  # Установка библиотеки для работы с PostgreSQL
    && rm -rf /var/lib/apt/lists/*  # Очистка кэша apt для уменьшения размера образа

# Копирование исходного кода приложения в контейнер
COPY app.py /app

# Установка Python-зависимостей, таких как psycopg2 для PostgreSQL, kafka-python для Kafka и Flask для веб-приложения
RUN pip install --no-cache-dir psycopg2 kafka-python flask

# Экспонирование порта 5000 для внешнего доступа (Flask по умолчанию работает на этом порту)
EXPOSE 5000

# Указание команды по умолчанию для запуска Flask-приложения
CMD ["python", "app.py"]
