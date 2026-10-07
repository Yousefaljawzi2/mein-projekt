# Big Data Analytics Assistant

Ein prüfungsorientiertes Big-Data-/KI-Projekt für E-Commerce-Daten.

Das System kombiniert:

- **1.000.000 Verkaufsdatensätze**
- **Apache Spark / PySpark**
- **strenge Datenbereinigung**
- **interaktives Streamlit-Dashboard**
- **LLM-gestützte Datenanalyse**
- **Trust Guard zur automatischen Prüfung von KI-Antworten**

## Projektidee

Das System analysiert große E-Commerce-Datenmengen und erlaubt anschließend Fragen in natürlicher Sprache.

Beispiele:

- Wie hoch ist der Gesamtumsatz?
- Welches Produkt erzielt den höchsten Umsatz?
- Welches Land ist am stärksten?
- Welcher Monat war am stärksten?
- Wie viele Ausreißer wurden erkannt?

Der entscheidende Punkt des Projekts ist nicht nur, eine LLM-Antwort zu erzeugen. Die Antwort wird anschließend mit deterministisch berechneten Referenzwerten verglichen.

Damit untersucht das Projekt auch die Frage:

> Wann können wir einer KI-Antwort vertrauen?

## Architektur

```text
data/sales_1m.csv
        |
        v
PySpark Datenbereinigung
        |
        v
Big-Data-Analytics
        |
        v
geprüfte Aggregationen
        |
        +--------------------+
        |                    |
        v                    v
Streamlit Dashboard       LLM Assistant
                             |
                             v
                         Trust Guard
                             |
                 +-----------+-----------+
                 |           |           |
               grün        gelb         rot
            verifiziert  unbekannt   widersprüchlich
```

## Datensatz

```text
data/sales_1m.csv
```

Der Datensatz enthält:

- 1.000.000 Datenzeilen
- 50.000 eindeutige Kunden
- Produkte und Kategorien
- Länder
- Bestellmengen
- Preise
- Zeitstempel

## Strenge Datenbereinigung

Die PySpark-Pipeline akzeptiert eine Zeile nur, wenn alle Datenqualitätsregeln erfüllt sind.

Geprüft werden unter anderem:

1. Pflichtfelder
2. Format der Bestell-ID
3. Format der Kunden-ID
4. doppelte Bestell-IDs
5. gültige Produkte
6. Produkt-/Kategorie-Konsistenz
7. erlaubte Länder
8. Mengen zwischen 1 und 50
9. positive Preise
10. plausible produktbezogene Preisbereiche
11. gültige Zeitstempel
12. Zeitraum 2024 bis 2025

Abgelehnte Zeilen werden nicht still gelöscht, sondern mit Begründung gespeichert:

```text
output/rejected_rows/
output/data_quality_report/
```

## Aktueller Datenqualitätsstand

Der mitgelieferte synthetische Datensatz wurde kontrolliert erzeugt.

```text
Eingelesene Zeilen: 1.000.000
Gültige Zeilen:     1.000.000
Abgelehnte Zeilen:  0
Qualitätsquote:     100 %
```

## Aktuelle Kennzahlen

Die im Dashboard hinterlegte, überprüfte Momentaufnahme basiert auf dem enthaltenen 1-Mio.-Datensatz.

```text
Bestellungen:                 1.000.000
Eindeutige Kunden:               50.000
Gesamtumsatz:             849.735.398,79 €
Ø Umsatz pro Bestellung:         849,74 €
3-Sigma-Ausreißer:                17.502
```

## LLM-Assistent

Die Datei

```text
src/llm_assistant.py
```

übergibt dem Sprachmodell nur bereits berechnete und geprüfte Aggregationen.

Das Modell wird ausdrücklich angewiesen:

- keine neuen Zahlen zu erfinden,
- keine unbelegten Ursachen zu behaupten,
- nur aus den bereitgestellten Fakten zu antworten,
- bei fehlender Evidenz dies klar zu sagen.

## Trust Guard

Die Datei

```text
src/trust_guard.py
```

prüft zentrale Aussagen des LLM automatisch.

Für wichtige Prüfungsfragen kennt das System die erwarteten Referenzwerte.

Beispiel:

```text
Frage:
Wie hoch ist der Gesamtumsatz?

LLM:
Der Gesamtumsatz beträgt 849.735.398,79 €.

Trust Guard:
🟢 VERIFIZIERT
```

Wenn das Modell stattdessen eine falsche Zahl nennt:

```text
LLM:
Der Gesamtumsatz beträgt 123 €.

Trust Guard:
🔴 NICHT VERIFIZIERT
```

Für Fragen ohne feste Prüfregel wird kein falsches Vertrauen erzeugt:

```text
🟡 NICHT AUTOMATISCH VERIFIZIERBAR
```

## Dashboard

Das Streamlit-Dashboard befindet sich in:

```text
app.py
```

Es enthält vier Bereiche:

1. **Dashboard**
   - KPIs
   - Umsatz nach Kategorie
   - Umsatz nach Land
   - Monatsverlauf
   - Top-Produkte

2. **KI-Assistent**
   - natürliche Fragen
   - LLM-Antwort
   - automatische Verifikation

3. **Datenqualität**
   - Anzahl gültiger und abgelehnter Zeilen
   - Bereinigungsregeln

4. **Methodik**
   - Erklärung der Vertrauenskette

## Installation

Voraussetzungen:

- Python 3.10+
- Java
- Apache Spark / PySpark

Installation:

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

## Big-Data-Analyse starten

```bash
spark-submit src/analytics.py --input data/sales_1m.csv --output output
```

## Dashboard starten

```bash
streamlit run app.py
```

Das Dashboard funktioniert auch ohne API-Key in einem verifizierbaren Demo-Modus.

## Echten LLM-Modus aktivieren

Kopiere zunächst:

```text
.env.example
```

Der echte API-Schlüssel darf **nicht** in GitHub committed werden.

Unter Linux/macOS:

```bash
export OPENAI_API_KEY="DEIN_API_KEY"
export OPENAI_MODEL="gpt-6-luna"
streamlit run app.py
```

Unter PowerShell:

```powershell
$env:OPENAI_API_KEY="DEIN_API_KEY"
$env:OPENAI_MODEL="gpt-6-luna"
streamlit run app.py
```

## Tests

Der Trust Guard besitzt automatische Tests.

```bash
python -m unittest tests/test_trust_guard.py
```

Getestet wird unter anderem:

- korrekte Antwort wird akzeptiert
- falscher Umsatz wird erkannt
- falsches Top-Produkt wird erkannt

## Projektstruktur

```text
mein-projekt/
├── app.py
├── data/
│   └── sales_1m.csv
├── dashboard_data/
│   ├── summary.json
│   ├── monthly_revenue.csv
│   ├── revenue_by_category.csv
│   ├── revenue_by_country.csv
│   └── top_products.csv
├── src/
│   ├── analytics.py
│   ├── generate_data.py
│   ├── llm_assistant.py
│   └── trust_guard.py
├── tests/
│   └── test_trust_guard.py
├── .env.example
├── requirements.txt
├── PROJECT_PITCH.md
└── README.md
```

## Prüfungsbezug

Das Projekt verbindet zwei Teile:

### 1. Bauen

Ein funktionierendes KI-Produkt mit:

- Big-Data-Verarbeitung
- Dashboard
- LLM-Integration
- natürlicher Sprache

### 2. Misstrauen und Prüfen

Das System demonstriert explizit, dass eine LLM-Antwort nicht automatisch richtig ist.

Die KI-Ausgabe wird gegen deterministische Datenwerte geprüft.

Damit lässt sich in der Prüfung zeigen:

- wo das LLM Mehrwert bringt,
- wo das LLM Fehler machen kann,
- welche Aussagen überprüfbar sind,
- wann eine Antwort nicht automatisch vertraut werden sollte.

## Grenzen des Projekts

Die Vertrauensprüfung deckt bewusst nur wichtige, vordefinierte Fragetypen automatisch ab.

Komplexe Warum-Fragen wie

> Warum war der Umsatz im Februar niedriger?

können durch die vorhandenen Verkaufsdaten nicht sicher kausal beantwortet werden.

Das System soll in diesem Fall keine Ursache erfinden, sondern fehlende Evidenz transparent machen.
