import json
import logging
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import sqlite3
import os

logging.basicConfig(level=logging.INFO)

# SQLite configuration
DB_NAME = os.getcwd() + "/database/weather_data.db"
JSON_PATH = os.getcwd() + "/database/weather_data.json"

# Kafka configuration
KAFKA_BROKER = "kafka:9092"  # Replace with "localhost:9092" for local testing
TOPIC = "weather"



def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature INTEGER,
            condition TEXT,
            timestamp INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(data):
    """Save weather data to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weather (city, temperature, condition, timestamp)
        VALUES (?, ?, ?, ?)
    """, (data["city"], data["temperature"], data["condition"], data["timestamp"]))
    conn.commit()
    conn.close()

# Сохранение данных в JSON
def save_to_json(data):
    # Если файл не существует, создаём его с пустым массивом
    if not os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'w') as file:
            json.dump([], file)

    # Чтение существующего содержимого
    with open(JSON_PATH, 'r') as file:
        weather_data = json.load(file)

    # Добавление нового сообщения
    weather_data.append(data)

    # Запись обратно в файл
    with open(JSON_PATH, 'w') as file:
        json.dump(weather_data, file, indent=4)

def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id=f'{TOPIC}-consumers',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logging.info("Connected to Kafka")
            return consumer
        except NoBrokersAvailable as e:
            logging.warning(f"Kafka broker not available ({e}), retrying in 5 seconds...")
            time.sleep(5)

consumer = create_consumer()
# Initialize SQLite database
init_db()



try:
    print("Starting consumer...")
    for message in consumer:
        weather_data = message.value
        logging.info(f"Received: {weather_data}")
        save_to_db(weather_data)
        save_to_json(weather_data)        
except KeyboardInterrupt:
     logging.info("Consumer stopped.")
finally:
    consumer.close()


