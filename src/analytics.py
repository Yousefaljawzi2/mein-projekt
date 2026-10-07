import argparse

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


SCHEMA = StructType(
    [
        StructField("order_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product", StringType(), True),
        StructField("category", StringType(), True),
        StructField("country", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("order_timestamp", StringType(), True),
    ]
)

VALID_COUNTRIES = [
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Netherlands",
    "Poland",
    "Austria",
    "Switzerland",
]

PRODUCT_RULES = {
    "Laptop": ("Electronics", 899.00),
    "Smartphone": ("Electronics", 649.00),
    "Headphones": ("Electronics", 89.00),
    "Monitor": ("Electronics", 279.00),
    "Keyboard": ("Electronics", 69.00),
    "Office Chair": ("Furniture", 229.00),
    "Desk": ("Furniture", 349.00),
    "Backpack": ("Accessories", 79.00),
    "Smartwatch": ("Accessories", 199.00),
    "Coffee Machine": ("Home", 149.00),
    "Vacuum Cleaner": ("Home", 219.00),
    "Running Shoes": ("Sports", 119.00),
}

MIN_TIMESTAMP = "2024-01-01 00:00:00"
MAX_TIMESTAMP = "2025-12-31 23:59:59"
MIN_QUANTITY = 1
MAX_QUANTITY = 50
PRICE_TOLERANCE = 0.20


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("BigDataEcommerceAnalytics")
        .getOrCreate()
    )


def _mapping_expr(index: int):
    pairs = []
    for product, rule in PRODUCT_RULES.items():
        pairs.extend([F.lit(product), F.lit(rule[index])])
    return F.create_map(*pairs)


def load_and_clean(spark: SparkSession, input_path: str):
    raw_df = (
        spark.read
        .option("header", True)
        .schema(SCHEMA)
        .csv(input_path)
    )

    input_rows = raw_df.count()

    # 1) Text standardisieren: führende/nachgestellte Leerzeichen entfernen.
    normalized = raw_df
    for column in ["order_id", "customer_id", "product", "category", "country", "order_timestamp"]:
        normalized = normalized.withColumn(column, F.trim(F.col(column)))

    expected_category = _mapping_expr(0)
    expected_base_price = _mapping_expr(1)

    prepared = (
        normalized
        .withColumn("_expected_category", expected_category[F.col("product")])
        .withColumn("_expected_base_price", expected_base_price[F.col("product")].cast("double"))
        .withColumn(
            "_parsed_timestamp",
            F.to_timestamp("order_timestamp", "yyyy-MM-dd HH:mm:ss"),
        )
        .withColumn(
            "_order_id_count",
            F.count("*").over(Window.partitionBy("order_id")),
        )
    )

    required_columns = [
        "order_id",
        "customer_id",
        "product",
        "category",
        "country",
        "quantity",
        "unit_price",
        "order_timestamp",
    ]

    missing_required = F.lit(False)
    for column in required_columns:
        condition = F.col(column).isNull()
        if column in ["order_id", "customer_id", "product", "category", "country", "order_timestamp"]:
            condition = condition | (F.col(column) == "")
        missing_required = missing_required | condition

    validation_errors = F.array_compact(
        F.array(
            F.when(missing_required, F.lit("missing_required_value")),
            F.when(
                F.col("order_id").isNotNull()
                & ~F.col("order_id").rlike(r"^ORD-[0-9]{9}$"),
                F.lit("invalid_order_id"),
            ),
            F.when(
                F.col("customer_id").isNotNull()
                & ~F.col("customer_id").rlike(r"^CUST-[0-9]{7}$"),
                F.lit("invalid_customer_id"),
            ),
            F.when(
                F.col("product").isNotNull()
                & F.col("_expected_category").isNull(),
                F.lit("invalid_product"),
            ),
            F.when(
                F.col("_expected_category").isNotNull()
                & (F.col("category") != F.col("_expected_category")),
                F.lit("category_product_mismatch"),
            ),
            F.when(
                F.col("country").isNotNull()
                & ~F.col("country").isin(VALID_COUNTRIES),
                F.lit("invalid_country"),
            ),
            F.when(
                F.col("quantity").isNotNull()
                & (
                    (F.col("quantity") < MIN_QUANTITY)
                    | (F.col("quantity") > MAX_QUANTITY)
                ),
                F.lit("invalid_quantity_range"),
            ),
            F.when(
                F.col("unit_price").isNotNull()
                & (
                    (F.col("unit_price") <= 0)
                    | F.isnan("unit_price")
                ),
                F.lit("invalid_unit_price"),
            ),
            F.when(
                F.col("_expected_base_price").isNotNull()
                & F.col("unit_price").isNotNull()
                & (
                    (F.col("unit_price") < F.col("_expected_base_price") * (1 - PRICE_TOLERANCE))
                    | (F.col("unit_price") > F.col("_expected_base_price") * (1 + PRICE_TOLERANCE))
                ),
                F.lit("price_outside_product_range"),
            ),
            F.when(
                F.col("order_timestamp").isNotNull()
                & F.col("_parsed_timestamp").isNull(),
                F.lit("invalid_timestamp"),
            ),
            F.when(
                F.col("_parsed_timestamp").isNotNull()
                & (
                    (F.col("_parsed_timestamp") < F.to_timestamp(F.lit(MIN_TIMESTAMP)))
                    | (F.col("_parsed_timestamp") > F.to_timestamp(F.lit(MAX_TIMESTAMP)))
                ),
                F.lit("timestamp_outside_expected_range"),
            ),
            F.when(
                F.col("order_id").isNotNull()
                & (F.col("_order_id_count") > 1),
                F.lit("duplicate_order_id"),
            ),
        )
    )

    validated = prepared.withColumn("validation_errors", validation_errors)

    clean_df = (
        validated
        .filter(F.size("validation_errors") == 0)
        .drop(
            "validation_errors",
            "_expected_category",
            "_expected_base_price",
            "_order_id_count",
            "order_timestamp",
        )
        .withColumnRenamed("_parsed_timestamp", "order_timestamp")
        .withColumn(
            "revenue",
            F.round(F.col("quantity") * F.col("unit_price"), 2),
        )
    )

    rejected_df = (
        validated
        .filter(F.size("validation_errors") > 0)
        .withColumn(
            "rejection_reasons",
            F.concat_ws("; ", F.col("validation_errors")),
        )
        .drop(
            "validation_errors",
            "_expected_category",
            "_expected_base_price",
            "_order_id_count",
            "_parsed_timestamp",
        )
    )

    quality_report = (
        validated
        .filter(F.size("validation_errors") > 0)
        .select(F.explode("validation_errors").alias("reason"))
        .groupBy("reason")
        .count()
        .orderBy(F.desc("count"), "reason")
    )

    clean_rows = clean_df.count()
    rejected_rows = input_rows - clean_rows

    print("\n=== Datenbereinigung ===")
    print(f"Eingelesene Zeilen: {input_rows:,}")
    print(f"Gültige Zeilen:     {clean_rows:,}")
    print(f"Abgelehnte Zeilen:  {rejected_rows:,}")
    if input_rows:
        print(f"Qualitätsquote:      {(clean_rows / input_rows) * 100:.2f}%")

    print("\n=== Ablehnungsgründe ===")
    quality_report.show(50, truncate=False)

    return clean_df, rejected_df, quality_report


def write_csv(df, path: str, single_file: bool = True):
    writer_df = df.coalesce(1) if single_file else df

    (
        writer_df.write
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
    write_csv(anomalies, f"{output_path}/anomalies", single_file=False)


def parse_args():
    parser = argparse.ArgumentParser(description="Big Data Analytics mit PySpark")
    parser.add_argument(
        "--input",
        default="data/sales_1m.csv",
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
        clean_df, rejected_df, quality_report = load_and_clean(spark, args.input)

        write_csv(
            quality_report,
            f"{args.output}/data_quality_report",
        )
        write_csv(
            rejected_df,
            f"{args.output}/rejected_rows",
            single_file=False,
        )

        run_analytics(clean_df, args.output)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
