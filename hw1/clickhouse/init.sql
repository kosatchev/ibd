CREATE TABLE IF NOT EXISTS customer_purchase (
    age Int32
    ,id UInt64  -- ClickHouse не поддерживает SERIAL, используем UInt64
    ,income Float64  -- Float в PostgreSQL соответствует Float64 в ClickHouse
    ,last_purchase_amount Float64
    ,membership_years Int32
    ,purchase_frequency Float64
    ,spending_score Float64
) ENGINE = MergeTree() 
ORDER BY id;  -- Указываем порядок сортировки для таблицы MergeTree

CREATE TABLE IF NOT EXISTS customers_transformed (
    age Int32
    ,average_income Float64  -- Float в PostgreSQL соответствует Float64 в ClickHouse
) ENGINE = MergeTree() 
ORDER BY average_income;