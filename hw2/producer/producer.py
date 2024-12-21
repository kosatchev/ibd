import json
import time
import random
import logging
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


logging.basicConfig(level=logging.INFO)


# Kafka configuration
KAFKA_BROKER = "kafka:9092"  # Replace with "localhost:9092" for local testing
TOPIC = "weather"

# Weather data generator
def generate_weather_data():
    cities = ["Moscow", "Saint Petersburg", "Krasnoyarsk", "Sochi", "Vladivostok"]
    conditions = ["sunny", "cloudy", "rainy", "snowy", "stormy"]

    return {
        "city": random.choice(cities),
        "temperature": random.randint(-30, 35),
        "condition": random.choice(conditions),
        "timestamp": int(time.time())
    }

# Initialize Kafka producer
def create_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=5
            )
            logging.info("Connected to Kafka")
            return producer
        except NoBrokersAvailable as e:
            logging.warning(f"Kafka broker not available ({e}), retrying in 5 seconds...")
            time.sleep(5)

producer = create_producer()

try:
    print("Starting producer...")
    while True:
        # Generate weather data
        weather_data = generate_weather_data()
        # Send data to Kafka topic
        producer.send(TOPIC, weather_data)
        logging.info(f"Sent: {weather_data}")
        time.sleep(2)  # Wait before sending the next message
except KeyboardInterrupt:
    logging.error("Producer stopped.")
finally:
    producer.close()