import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    DoubleType,
)


SCHEMA = StructType(
    [
        StructField("order_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("product", StringType(), False),
        StructField("category", StringType(), False),
        StructField("country", StringType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("unit_price", DoubleType(), False),
        StructField("order_timestamp", StringType(), False),
    ]
)


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("BigDataEcommerceAnalytics")
        .getOrCreate()
    )


def load_and_clean(spark: SparkSession, input_path: str):
    df = (
        spark.read
        .option("header", True)
        .schema(SCHEMA)
        .csv(input_path)
    )

    return (
        df.dropna()
        .filter((F.col("quantity") > 0) & (F.col("unit_price") >= 0))
        .withColumn(
            "order_timestamp",
            F.to_timestamp("order_timestamp", "yyyy-MM-dd HH:mm:ss"),
        )
        .withColumn(
            "revenue",
            F.round(F.col("quantity") * F.col("unit_price"), 2),
        )
    )


def write_csv(df, path: str):
    (
        df.coalesce(1)
        .write
        .mode("overwrite")
        .option("header", True)
        .csv(path)
    )


def run_analytics(df, output_path: str):
    kpis = df.agg(
        F.countDistinct("order_id").alias("total_orders"),
        F.countDistinct("customer_id").alias("unique_customers"),
        F.round(F.sum("revenue"), 2).alias("total_revenue"),
        F.round(F.avg("revenue"), 2).alias("average_order_revenue"),
    )

    revenue_by_category = (
        df.groupBy("category")
        .agg(
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.countDistinct("order_id").alias("orders"),
        )
        .orderBy(F.desc("revenue"))
    )

    revenue_by_country = (
        df.groupBy("country")
        .agg(
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.countDistinct("customer_id").alias("customers"),
        )
        .orderBy(F.desc("revenue"))
    )

    monthly_revenue = (
        df.withColumn("month", F.date_format("order_timestamp", "yyyy-MM"))
        .groupBy("month")
        .agg(
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.countDistinct("order_id").alias("orders"),
        )
        .orderBy("month")
    )

    top_products = (
        df.groupBy("product", "category")
        .agg(
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.sum("quantity").alias("units_sold"),
        )
        .orderBy(F.desc("revenue"))
        .limit(20)
    )

    stats = df.agg(
        F.avg("revenue").alias("mean_revenue"),
        F.stddev("revenue").alias("std_revenue"),
    ).first()

    mean_revenue = stats["mean_revenue"] or 0.0
    std_revenue = stats["std_revenue"] or 0.0
    threshold = mean_revenue + (3 * std_revenue)

    anomalies = (
        df.filter(F.col("revenue") > F.lit(threshold))
        .select(
            "order_id",
            "customer_id",
            "product",
            "category",
            "country",
            "quantity",
            "unit_price",
            "revenue",
            "order_timestamp",
        )
        .orderBy(F.desc("revenue"))
    )

    print("\n=== KPIs ===")
    kpis.show(truncate=False)

    print("\n=== Top Kategorien ===")
    revenue_by_category.show(10, truncate=False)

    print("\n=== Top Länder ===")
    revenue_by_country.show(10, truncate=False)

    print("\n=== Top Produkte ===")
    top_products.show(10, truncate=False)

    write_csv(kpis, f"{output_path}/kpis")
    write_csv(revenue_by_category, f"{output_path}/revenue_by_category")
    write_csv(revenue_by_country, f"{output_path}/revenue_by_country")
    write_csv(monthly_revenue, f"{output_path}/monthly_revenue")
    write_csv(top_products, f"{output_path}/top_products")
    write_csv(anomalies, f"{output_path}/anomalies")


def parse_args():
    parser = argparse.ArgumentParser(description="Big Data Analytics mit PySpark")
    parser.add_argument(
        "--input",
        default="data/sales.csv",
        help="Pfad zur Eingabe-CSV",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Zielordner für Analyse-Ergebnisse",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    spark = build_spark()

    try:
        df = load_and_clean(spark, args.input)
        print(f"Geladene Datensätze: {df.count():,}")
        run_analytics(df, args.output)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
