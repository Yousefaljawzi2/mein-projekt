import argparse
import csv
import os
import random
from datetime import datetime, timedelta


PRODUCTS = [
    ("Laptop", "Electronics", 899.00),
    ("Smartphone", "Electronics", 649.00),
    ("Headphones", "Electronics", 89.00),
    ("Monitor", "Electronics", 279.00),
    ("Keyboard", "Electronics", 69.00),
    ("Office Chair", "Furniture", 229.00),
    ("Desk", "Furniture", 349.00),
    ("Backpack", "Accessories", 79.00),
    ("Smartwatch", "Accessories", 199.00),
    ("Coffee Machine", "Home", 149.00),
    ("Vacuum Cleaner", "Home", 219.00),
    ("Running Shoes", "Sports", 119.00),
]

COUNTRIES = [
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Netherlands",
    "Poland",
    "Austria",
    "Switzerland",
]

START = datetime(2024, 1, 1)
END = datetime(2025, 12, 31, 23, 59, 59)


def random_timestamp():
    seconds = int((END - START).total_seconds())
    return START + timedelta(seconds=random.randint(0, seconds))


def generate(rows: int, output_path: str, seed: int):
    random.seed(seed)

    directory = os.path.dirname(output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "order_id",
                "customer_id",
                "product",
                "category",
                "country",
                "quantity",
                "unit_price",
                "order_timestamp",
            ]
        )

        for index in range(1, rows + 1):
            product, category, base_price = random.choice(PRODUCTS)
            quantity = random.randint(1, 5)

            price_factor = random.uniform(0.85, 1.15)
            unit_price = round(base_price * price_factor, 2)

            # Seltene große Bestellungen erzeugen interessante Ausreißer.
            if random.random() < 0.002:
                quantity = random.randint(20, 50)

            writer.writerow(
                [
                    f"ORD-{index:09d}",
                    f"CUST-{random.randint(1, max(1000, rows // 20)):07d}",
                    product,
                    category,
                    random.choice(COUNTRIES),
                    quantity,
                    unit_price,
                    random_timestamp().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            if index % 100000 == 0:
                print(f"{index:,} Datensätze erzeugt")

    print(f"Fertig: {rows:,} Datensätze in {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Erzeugt synthetische E-Commerce-Daten"
    )
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--output", default="data/sales.csv")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(args.rows, args.output, args.seed)
