import os
import logging  # Импортируем модуль для логирования
from pyspark.sql import SparkSession  # Импортируем SparkSession для создания и управления сессией Spark
from pyspark.sql.functions import from_json, col, expr, regexp_extract, concat_ws, split, column  # Импортируем функции PySpark для обработки данных
from pyspark.sql.types import StructType, IntegerType, FloatType, StructField  # Импортируем типы данных и схемы для структурированных данных

# Задаем параметры подключения к Kafka
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Адрес брокера Kafka
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "customers")  # Название топика для чтения данных из Kafka

# Задаем параметры подключения к ClickHouse
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")  # Хост ClickHouse
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))  # Порт ClickHouse
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")  # Название базы данных ClickHouse
CLICKHOUSE_TABLE = os.getenv("CLICKHOUSE_TABLE", "customer_purchase")  # Название таблицы ClickHouse

# Драйвер для подключения к ClickHouse
driver = "com.clickhouse.jdbc.ClickHouseDriver"  # Указываем драйвер для ClickHouse JDBC

# Настраиваем логирование
logging.basicConfig(  # Настройка формата логов и уровня логирования
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)  # Создаем объект логера


def save_to_clickhouse(partition_data):  # Функция для сохранения данных в ClickHouse
    partition_data.show(truncate=True)  # Вывод данных в консоль для проверки
    try:
        # Настройка и выполнение записи данных в ClickHouse
        partition_data.write \
            .format("jdbc") \
            .option('driver', driver) \
            .option("url", f"jdbc:clickhouse://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{CLICKHOUSE_DATABASE}") \
            .option("dbtable", CLICKHOUSE_TABLE) \
            .mode("append") \
            .save()
        logger.info(f"Data has been successfully written to {CLICKHOUSE_DATABASE}.{CLICKHOUSE_TABLE}.")
    except Exception as e:  # Обработка ошибок записи
        logger.error(f"Error writing data to ClickHouse: {e}")


def main():  # Основная функция
    # Создаем сессию Spark
    spark = SparkSession.builder \
        .appName("Spark consumer") \
        .master("local[*]") \
        .getOrCreate()

    # Читаем данные из Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .load()

    # Парсинг JSON-данных из Kafka
    parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_data")  # Преобразуем сообщения Kafka в строки JSON
    df_extracted = parsed_df.select(  # Извлекаем отдельные поля из JSON-данных
        regexp_extract("json_data", r'"age":\s*([\d.]+)', 1).alias("age"),
        regexp_extract("json_data", r'"id":\s*([\d.]+)', 1).alias("id"),
        regexp_extract("json_data", r'"income":\s*([\d.]+)', 1).alias("income"),
        regexp_extract("json_data", r'"last_purchase_amount":\s*([\d.]+)', 1).alias("last_purchase_amount"),
        regexp_extract("json_data", r'"membership_years":\s*([\d.]+)', 1).alias("membership_years"),
        regexp_extract("json_data", r'"purchase_frequency":\s*([\d.]+)', 1).alias("purchase_frequency"),
        regexp_extract("json_data", r'"spending_score":\s*([\d.]+)', 1).alias("spending_score"),
    )
    # Формируем окончательный DataFrame
    df_final = df_extracted.select(
        concat_ws(" ", *[col for col in df_extracted.columns]).alias("space_separated_values")
    ).select(split(column("space_separated_values"), " ").alias("split_values")) \
    .select(
        column("split_values").getItem(0).cast(IntegerType()).alias("age"),
        column("split_values").getItem(1).cast(IntegerType()).alias("id"),
        column("split_values").getItem(2).cast(FloatType()).alias("income"),
        column("split_values").getItem(3).cast(FloatType()).alias("last_purchase_amount"),
        column("split_values").getItem(4).cast(IntegerType()).alias("membership_years"),
        column("split_values").getItem(5).cast(FloatType()).alias("purchase_frequency"),
        column("split_values").getItem(6).cast(FloatType()).alias("spending_score"),
    )
    # Настройка записи данных в ClickHouse с использованием foreachBatch
    df_final.writeStream \
        .foreachBatch(lambda df, _: save_to_clickhouse(df)) \
        .start() \
        .awaitTermination()

if __name__ == "__main__":  # Проверка на выполнение скрипта напрямую
    main()  # Запуск основной функции