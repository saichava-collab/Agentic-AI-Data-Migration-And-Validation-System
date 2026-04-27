from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Callable, TypeVar

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

from utils.io_helpers import ensure_dir, load_yaml, write_json

T = TypeVar("T")

STATUS_MAPPING = {
    "DONE": "completed",
    "PENDING_APPROVAL": "pending",
    "FAILED": "cancelled",
}

COUNTRY_MAPPING = {
    "usa": "USA",
    "uk": "UK",
    "uae": "UAE",
    "mexico": "Mexico",
    "india": "India",
}


def load_orders_from_sqlite(sqlite_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(sqlite_path)
    try:
        return pd.read_sql_query("SELECT * FROM orders", conn)
    finally:
        conn.close()


def benchmark_step(fn: Callable[[], T]) -> tuple[T, float]:
    start = time.perf_counter()
    result = fn()
    elapsed = round(time.perf_counter() - start, 4)
    return result, elapsed


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    spark_cfg = config["spark"]
    output_dir = Path(config["paths"]["output_dir"])
    ensure_dir(output_dir)

    spark = (
        SparkSession.builder.appName(spark_cfg["app_name"])
        .master(spark_cfg["master"])
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    customers = spark.read.option("header", True).csv(config["paths"]["source_csv"])

    orders_pd = load_orders_from_sqlite(config["paths"]["source_sqlite"])
    order_schema = StructType(
        [
            StructField("order_id", IntegerType(), False),
            StructField("customer_ref", IntegerType(), False),
            StructField("product_name", StringType(), True),
            StructField("order_amount", DoubleType(), True),
            StructField("order_status", StringType(), True),
            StructField("created_at", StringType(), True),
        ]
    )
    orders = spark.createDataFrame(orders_pd, schema=order_schema)

    migrated_customers = (
        customers.withColumn("customer_id", F.col("customer_id").cast("int"))
        .withColumn("full_name", F.initcap(F.trim(F.col("full_name"))))
        .withColumn("email", F.lower(F.trim(F.col("email"))))
        .withColumn("country", F.lower(F.trim(F.col("country"))))
        .replace(COUNTRY_MAPPING, subset=["country"])
        .withColumn("signup_ts", F.to_timestamp("signup_ts"))
        .dropDuplicates(["customer_id"])
    )

    migrated_orders = (
        orders.withColumnRenamed("customer_ref", "customer_id")
        .withColumn("product_name", F.initcap(F.trim(F.col("product_name"))))
        .withColumn("normalized_status", F.create_map([F.lit(x) for kv in STATUS_MAPPING.items() for x in kv])[F.col("order_status")])
        .withColumn("created_at", F.to_timestamp("created_at"))
    )

    customer_order_360 = (
        migrated_orders.join(migrated_customers, on="customer_id", how="left")
        .select(
            "customer_id",
            "full_name",
            "email",
            "country",
            "signup_ts",
            "order_id",
            "product_name",
            "order_amount",
            "order_status",
            "normalized_status",
            "created_at",
        )
        .orderBy("customer_id", "order_id")
    )

    # Reproducible optimization artifact: compare default execution with a partitioned, cached plan.
    baseline_count, baseline_seconds = benchmark_step(lambda: customer_order_360.count())
    optimized_df = customer_order_360.repartition(4, "customer_id").cache()
    optimized_count, optimized_seconds = benchmark_step(lambda: optimized_df.count())

    migrated_customers.write.mode("overwrite").parquet(str(output_dir / "migrated_customers.parquet"))
    migrated_orders.write.mode("overwrite").parquet(str(output_dir / "migrated_orders.parquet"))
    optimized_df.write.mode("overwrite").parquet(str(output_dir / "customer_order_360.parquet"))
    optimized_df.toPandas().to_csv(output_dir / "customer_order_360.csv", index=False)

    customers_count = migrated_customers.count()
    orders_count = migrated_orders.count()
    throughput_improvement_pct = round(((baseline_seconds - optimized_seconds) / baseline_seconds) * 100, 2) if baseline_seconds else 0.0

    benchmark_report = {
        "baseline_strategy": "default Spark execution plan",
        "optimized_strategy": "repartition by customer_id and cache before downstream actions",
        "baseline_seconds": baseline_seconds,
        "optimized_seconds": optimized_seconds,
        "baseline_records": baseline_count,
        "optimized_records": optimized_count,
        "throughput_improvement_pct": throughput_improvement_pct,
        "processing_cost_reduction_proxy_pct": max(0.0, throughput_improvement_pct),
        "note": "Runtime varies by machine. The file documents the exact local measurement for interview discussion.",
    }
    write_json(output_dir / "performance_benchmark.json", benchmark_report)

    print("Batch migration completed successfully")
    print(f"Migrated customers: {customers_count}")
    print(f"Migrated orders: {orders_count}")
    print(f"Joined customer-order records: {optimized_count}")
    print(f"Baseline seconds: {baseline_seconds}")
    print(f"Optimized seconds: {optimized_seconds}")
    print(f"Measured throughput improvement: {throughput_improvement_pct}%")

    spark.stop()


if __name__ == "__main__":
    main()
