import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col

# Задаем параметры подключения к ClickHouse
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")  # Хост ClickHouse
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))  # Порт ClickHouse
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")  # Название базы данных ClickHouse
CLICKHOUSE_INPUT_TABLE = os.getenv("CLICKHOUSE_INPUT_TABLE", "customer_purchase")  # Название таблицы для чтения
CLICKHOUSE_OUTPUT_TABLE = os.getenv("CLICKHOUSE_OUTPUT_TABLE", "customers_transformed")  # Название таблицы для записи

# Драйвер для подключения к ClickHouse
driver = "com.clickhouse.jdbc.ClickHouseDriver"

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def save_to_clickhouse(df):
    try:
        # Сохранение результатов в ClickHouse
        df.write \
            .format("jdbc") \
            .option('driver', driver) \
            .option("url", f"jdbc:clickhouse://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{CLICKHOUSE_DATABASE}") \
            .option("dbtable", CLICKHOUSE_OUTPUT_TABLE) \
            .mode("append") \
            .save()
        logger.info(f"Data has been successfully written to {CLICKHOUSE_DATABASE}.{CLICKHOUSE_OUTPUT_TABLE}.")
    except Exception as e:
        logger.error(f"Error writing data to ClickHouse: {e}")

def main():
    # Создаем сессию Spark
    spark = SparkSession.builder \
        .appName("Spark ClickHouse Average Income") \
        .master("local[*]") \
        .getOrCreate()

    # Читаем данные из ClickHouse
    input_df = spark.read \
        .format("jdbc") \
        .option("driver", driver) \
        .option("url", f"jdbc:clickhouse://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{CLICKHOUSE_DATABASE}") \
        .option("dbtable", CLICKHOUSE_INPUT_TABLE) \
        .load()

    # Расчет среднего дохода для каждого возраста
    avg_income_df = input_df.groupBy("age").agg(avg("income").alias("average_income"))

    # Сохраняем результаты в ClickHouse
    save_to_clickhouse(avg_income_df)

if __name__ == "__main__":
    main()