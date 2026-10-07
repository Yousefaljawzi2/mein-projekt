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

Der enthaltene 1-Millionen-Datensatz ist jetzt die Standardeingabe:

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

Der Datensatz ist reproduzierbar. Mit folgendem Befehl können wieder genau 1.000.000 synthetische Zeilen erzeugt werden:

```bash
python src/generate_data.py --rows 1000000 --output data/sales_1m.csv
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

Das Projekt verwendet Spark DataFrames statt einer rein lokalen In-Memory-Verarbeitung. Dadurch kann dieselbe Logik lokal oder verteilt auf einem Spark-Cluster mit wesentlich größeren Datenmengen ausgeführt werden.

Mögliche Erweiterungen:

- Speicherung in Parquet statt CSV
- Verarbeitung mit Apache Kafka
- Datenhaltung in HDFS oder S3
- Spark Structured Streaming
- Dashboard mit Power BI, Tableau oder Streamlit
- Machine Learning mit Spark MLlib
