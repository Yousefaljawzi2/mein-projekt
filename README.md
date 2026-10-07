# Big Data Analytics mit PySpark

Dieses Projekt demonstriert eine skalierbare Big-Data-Analyse für E-Commerce-Verkaufsdaten mit **Apache Spark / PySpark**.

## Ziel

Die Pipeline verarbeitet große Mengen von Bestelldaten und beantwortet unter anderem:

- Wie hoch ist der Gesamtumsatz?
- Welche Kategorien erzielen den meisten Umsatz?
- Welche Länder sind die stärksten Märkte?
- Wie entwickelt sich der Umsatz pro Monat?
- Welche Produkte verkaufen sich am besten?
- Welche Bestellungen sind ungewöhnlich groß und können als Ausreißer betrachtet werden?

## Projektstruktur

```text
mein-projekt/
├── src/
│   ├── generate_data.py
│   └── analytics.py
├── data/
├── output/
├── requirements.txt
├── .gitignore
└── README.md
```

## Voraussetzungen

- Python 3.10+
- Java für Apache Spark
- PySpark

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Unter Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## 1. Testdaten erzeugen

100.000 Datensätze:

```bash
python src/generate_data.py --rows 100000 --output data/sales.csv
```

Für einen größeren Big-Data-Test, zum Beispiel 1 Million Datensätze:

```bash
python src/generate_data.py --rows 1000000 --output data/sales.csv
```

## 2. Analyse starten

```bash
spark-submit src/analytics.py --input data/sales.csv --output output
```

Alternativ lokal:

```bash
python src/analytics.py --input data/sales.csv --output output
```

## Analysen

Die Spark-Pipeline berechnet:

1. Gesamtzahl der Bestellungen
2. Anzahl eindeutiger Kunden
3. Gesamtumsatz
4. Durchschnittlichen Umsatz pro Bestellung
5. Umsatz pro Kategorie
6. Umsatz pro Land
7. Monatliche Umsatzentwicklung
8. Top-Produkte nach Umsatz
9. Auffällige Bestellungen auf Basis einer 3-Sigma-Regel

## Ergebnisse

Die Resultate werden als CSV-Dateien in Unterordnern von `output/` gespeichert:

```text
output/
├── kpis/
├── revenue_by_category/
├── revenue_by_country/
├── monthly_revenue/
├── top_products/
└── anomalies/
```

## Big-Data-Aspekte

Das Projekt verwendet Spark DataFrames statt einer rein lokalen In-Memory-Verarbeitung. Dadurch kann dieselbe Logik lokal auf kleinen Testdaten oder verteilt auf einem Spark-Cluster mit wesentlich größeren Datenmengen ausgeführt werden.

Mögliche Erweiterungen:

- Speicherung in Parquet statt CSV
- Verarbeitung mit Apache Kafka
- Datenhaltung in HDFS oder S3
- Spark Structured Streaming
- Dashboard mit Power BI, Tableau oder Streamlit
- Machine Learning mit Spark MLlib
