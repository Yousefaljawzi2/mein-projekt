import json
import unittest
from pathlib import Path

import pandas as pd

from src.trust_guard import reference_answer, verify_answer


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "dashboard_data"


def load_data():
    with open(DATA_DIR / "summary.json", "r", encoding="utf-8") as handle:
        summary = json.load(handle)

    return {
        "summary": summary,
        "categories": pd.read_csv(DATA_DIR / "revenue_by_category.csv"),
        "countries": pd.read_csv(DATA_DIR / "revenue_by_country.csv"),
        "monthly": pd.read_csv(DATA_DIR / "monthly_revenue.csv"),
        "products": pd.read_csv(DATA_DIR / "top_products.csv"),
    }


class TrustGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()

    def test_reference_answer_is_verified(self):
        question = "Wie hoch ist der Gesamtumsatz?"
        answer = reference_answer(question, self.data)
        result = verify_answer(question, answer, self.data)
        self.assertEqual(result["status"], "verified")

    def test_wrong_revenue_is_rejected(self):
        question = "Wie hoch ist der Gesamtumsatz?"
        answer = "Der Gesamtumsatz beträgt 123,00 €."
        result = verify_answer(question, answer, self.data)
        self.assertEqual(result["status"], "failed")

    def test_wrong_top_product_is_rejected(self):
        question = "Welches Produkt erzielt den höchsten Umsatz?"
        answer = "Smartphone erzielt mit 165.816.628,80 € den höchsten Umsatz."
        result = verify_answer(question, answer, self.data)
        self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main()
