# Big Data Analytics mit PySpark

Dieses Projekt demonstriert eine skalierbare Big-Data-Analyse für E-Commerce-Verkaufsdaten mit **Apache Spark / PySpark**.

## Datensatz

Der große Testdatensatz ist bereits im Repository enthalten:

```text
data/sales_1m.csv
```

Er enthält **1.000.000 Datenzeilen** (plus Kopfzeile) und umfasst Bestellungen mit Kunden, Produkten, Kategorien, Ländern, Mengen, Preisen und Zeitstempeln.

## Ziel

Die Pipeline verarbeitet große Mengen von Bestelldaten und beantwortet unter anderem:

- Wie hoch ist der Gesamtumsatz?
- Welche Kategorien erzielen den meisten Umsatz?
- Welche Länder sind die stärksten Märkte?
- Wie entwickelt sich der Umsatz pro Monat?
- Welche Produkte verkaufen sich am besten?
- Welche Bestellungen sind ungewöhnlich groß und können als Ausreißer betrachtet werden?

## Strenge Datenbereinigung

Vor jeder Analyse wird der Datensatz anhand eines festen Datenvertrags validiert. Eine Zeile wird nur übernommen, wenn **alle** Regeln erfüllt sind.

Geprüft werden:

1. Pflichtfelder dürfen nicht fehlen oder leer sein.
2. `order_id` muss dem Muster `ORD-#########` entsprechen.
3. `customer_id` muss dem Muster `CUST-#######` entsprechen.
4. `order_id` muss eindeutig sein; doppelte IDs werden abgelehnt.
5. Produkte müssen aus dem definierten Produktkatalog stammen.
6. Produkt und Kategorie müssen zueinander passen.
7. Länder müssen aus der erlaubten Länderliste stammen.
8. Die Bestellmenge muss zwischen 1 und 50 liegen.
9. Preise müssen positiv und numerisch sein.
10. Der Preis muss innerhalb von ±20 % des Referenzpreises des Produkts liegen.
11. Zeitstempel müssen korrekt parsebar sein.
12. Zeitstempel müssen innerhalb des erwarteten Datenzeitraums 2024–2025 liegen.
13. Textwerte werden vor der Validierung mit `trim()` normalisiert.

Abgelehnte Zeilen werden **nicht still verworfen**. Sie werden mit ihren Fehlergründen gespeichert:

```text
output/rejected_rows/
output/data_quality_report/
```

Damit bleibt die Datenbereinigung vollständig nachvollziehbar und auditierbar.

## Projektstruktur

```text
mein-projekt/
├── data/
│   └── sales_1m.csv
├── src/
│   ├── generate_data.py
│   └── analytics.py
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

## Analyse starten

Der enthaltene 1-Millionen-Datensatz ist die Standardeingabe:

```bash
spark-submit src/analytics.py
```

Alternativ:

```bash
python src/analytics.py
```

Mit expliziten Pfaden:

```bash
spark-submit src/analytics.py --input data/sales_1m.csv --output output
```

## Datensatz neu erzeugen

Der Datensatz ist reproduzierbar:

```bash
python src/generate_data.py --rows 1000000 --output data/sales_1m.csv
```

## Analysen

Nach der Bereinigung berechnet die Spark-Pipeline:

1. Gesamtzahl der gültigen Bestellungen
2. Anzahl eindeutiger Kunden
3. Gesamtumsatz
4. Durchschnittlichen Umsatz pro Bestellung
5. Umsatz pro Kategorie
6. Umsatz pro Land
7. Monatliche Umsatzentwicklung
8. Top-Produkte nach Umsatz
9. Auffällige Bestellungen auf Basis einer 3-Sigma-Regel

## Ergebnisse

```text
output/
├── data_quality_report/
├── rejected_rows/
├── kpis/
├── revenue_by_category/
├── revenue_by_country/
├── monthly_revenue/
├── top_products/
└── anomalies/
```

## Big-Data-Aspekte

Das Projekt verwendet Spark DataFrames und Spark Window Functions. Aggregationen, Validierung und Datenqualitätsprüfung können damit verteilt auf einem Spark-Cluster ausgeführt werden.

Mögliche Erweiterungen:

- Speicherung in Parquet statt CSV
- Verarbeitung mit Apache Kafka
- Datenhaltung in HDFS oder S3
- Spark Structured Streaming
- Dashboard mit Power BI, Tableau oder Streamlit
- Machine Learning mit Spark MLlib
