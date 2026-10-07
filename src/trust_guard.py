import re


def _euro(value):
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _int(value):
    return f"{int(value):,}".replace(",", ".")


def _intent(question: str):
    q = question.lower()

    if "gesamtumsatz" in q or ("umsatz" in q and "gesamt" in q):
        return "total_revenue"
    if ("produkt" in q) and any(word in q for word in ["höch", "beste", "stärk", "meist"]):
        return "top_product"
    if ("land" in q) and any(word in q for word in ["höch", "beste", "stärk", "meist"]):
        return "top_country"
    if ("kategorie" in q) and any(word in q for word in ["höch", "beste", "stärk", "meist"]):
        return "top_category"
    if "monat" in q and any(word in q for word in ["stärk", "höch", "beste"]):
        return "best_month"
    if "monat" in q and any(word in q for word in ["schwäch", "niedrig", "schlecht"]):
        return "worst_month"
    if "ausreißer" in q or "ausreisser" in q:
        return "anomalies"
    if "kunde" in q and any(word in q for word in ["wie viele", "anzahl", "eindeutig"]):
        return "unique_customers"
    if "bestellung" in q and any(word in q for word in ["wie viele", "anzahl"]):
        return "total_orders"
    if "durchschnitt" in q and "umsatz" in q:
        return "average_order_revenue"
    return None


def _expected(intent: str, data: dict):
    summary = data["summary"]

    if intent == "total_revenue":
        return {"label": "Gesamtumsatz", "name": None, "value": float(summary["kpis"]["total_revenue"]), "type": "money"}
    if intent == "average_order_revenue":
        return {"label": "Durchschnittlicher Bestellumsatz", "name": None, "value": float(summary["kpis"]["average_order_revenue"]), "type": "money"}
    if intent == "unique_customers":
        return {"label": "Eindeutige Kunden", "name": None, "value": int(summary["kpis"]["unique_customers"]), "type": "integer"}
    if intent == "total_orders":
        return {"label": "Bestellungen", "name": None, "value": int(summary["kpis"]["total_orders"]), "type": "integer"}
    if intent == "anomalies":
        return {"label": "Ausreißer", "name": None, "value": int(summary["anomalies"]["count"]), "type": "integer"}
    if intent == "top_product":
        item = summary["leaders"]["top_product"]
        return {"label": "Top-Produkt", "name": item["name"], "value": float(item["revenue"]), "type": "money"}
    if intent == "top_country":
        item = summary["leaders"]["top_country"]
        return {"label": "Top-Land", "name": item["name"], "value": float(item["revenue"]), "type": "money"}
    if intent == "top_category":
        item = summary["leaders"]["top_category"]
        return {"label": "Top-Kategorie", "name": item["name"], "value": float(item["revenue"]), "type": "money"}
    if intent == "best_month":
        item = summary["leaders"]["best_month"]
        return {"label": "Stärkster Monat", "name": item["month"], "value": float(item["revenue"]), "type": "money"}
    if intent == "worst_month":
        item = summary["leaders"]["worst_month"]
        return {"label": "Schwächster Monat", "name": item["month"], "value": float(item["revenue"]), "type": "money"}
    return None


def _extract_numbers(text: str):
    pattern = re.compile(
        r"(?<![\w-])(\d[\d\.\,\s]*\d|\d)\s*(mio\.?|million(?:en)?|mrd\.?|milliarde(?:n)?)?",
        re.IGNORECASE,
    )
    values = []

    for raw, unit in pattern.findall(text):
        token = raw.replace(" ", "")

        if "." in token and "," in token:
            if token.rfind(",") > token.rfind("."):
                token = token.replace(".", "").replace(",", ".")
            else:
                token = token.replace(",", "")
        elif "," in token:
            parts = token.split(",")
            if len(parts[-1]) <= 2:
                token = token.replace(".", "").replace(",", ".")
            else:
                token = token.replace(",", "")
        elif token.count(".") > 1:
            token = token.replace(".", "")
        elif token.count(".") == 1:
            left, right = token.split(".")
            if len(right) == 3 and len(left) >= 1:
                token = left + right

        try:
            value = float(token)
        except ValueError:
            continue

        u = unit.lower()
        if u.startswith("mio") or u.startswith("million"):
            value *= 1_000_000
        elif u.startswith("mrd") or u.startswith("milliarde"):
            value *= 1_000_000_000

        values.append(value)

    return values


def _number_matches(expected, answer, expected_type):
    numbers = _extract_numbers(answer)

    if expected_type == "integer":
        return any(abs(value - expected) < 0.5 for value in numbers)

    tolerance = max(1.0, abs(expected) * 0.005)
    return any(abs(value - expected) <= tolerance for value in numbers)


def verify_answer(question: str, answer: str, data: dict) -> dict:
    intent = _intent(question)

    if not intent:
        return {
            "status": "not_verifiable",
            "reason": "Für diese Frage ist keine feste automatische Prüfregel hinterlegt.",
        }

    expected = _expected(intent, data)
    name_ok = True

    if expected["name"]:
        name_ok = expected["name"].lower() in answer.lower()

    number_ok = _number_matches(expected["value"], answer, expected["type"])

    return {
        "status": "verified" if name_ok and number_ok else "failed",
        "intent": intent,
        "expected_label": expected["label"],
        "expected_name": expected["name"],
        "expected_value": expected["value"],
        "name_match": name_ok,
        "number_match": number_ok,
    }


def reference_answer(question: str, data: dict) -> str:
    intent = _intent(question)

    if not intent:
        return (
            "Diese Frage ist in der aktuellen Demo nicht als automatisch verifizierbare "
            "Standardfrage hinterlegt. Im LLM-Modus kann sie beantwortet werden, sofern "
            "sie durch die bereitgestellten Aggregationen belegt ist."
        )

    expected = _expected(intent, data)
    value = _euro(expected["value"]) if expected["type"] == "money" else _int(expected["value"])

    if intent == "total_revenue":
        return f"Der Gesamtumsatz beträgt {value}."
    if intent == "average_order_revenue":
        return f"Der durchschnittliche Umsatz pro Bestellung beträgt {value}."
    if intent == "unique_customers":
        return f"Der Datensatz enthält {value} eindeutige Kunden."
    if intent == "total_orders":
        return f"Der Datensatz enthält {value} Bestellungen."
    if intent == "anomalies":
        threshold = data["summary"]["anomalies"]["threshold"]
        return f"Die 3-Sigma-Prüfung erkennt {value} Ausreißer. Die Umsatzgrenze liegt bei {_euro(threshold)}."
    if intent == "top_product":
        return f"{expected['name']} erzielt mit {value} den höchsten Produktumsatz."
    if intent == "top_country":
        return f"{expected['name']} hat mit {value} den höchsten Länderumsatz."
    if intent == "top_category":
        return f"{expected['name']} ist mit {value} die umsatzstärkste Kategorie."
    if intent == "best_month":
        return f"{expected['name']} ist mit {value} der umsatzstärkste Monat."
    if intent == "worst_month":
        return f"{expected['name']} ist mit {value} der umsatzschwächste Monat."

    return "Für diese Frage liegt keine Referenzantwort vor."
