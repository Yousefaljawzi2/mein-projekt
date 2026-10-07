# Projekt-Pitch – Big Data Analytics Assistant

## Elevator Pitch

Wir haben einen Big Data Analytics Assistant entwickelt, der eine Million E-Commerce-Datensätze mit PySpark verarbeitet und die Ergebnisse in einem interaktiven Dashboard darstellt.

Der Nutzer kann anschließend in natürlicher Sprache Fragen an die Daten stellen.

Der besondere Teil unseres Projekts ist ein Trust Guard: Wir vertrauen der LLM-Antwort nicht automatisch, sondern vergleichen zentrale Aussagen mit deterministisch berechneten Referenzwerten.

Damit verbindet das Projekt Big Data, KI und die Frage, wann man einem KI-Ergebnis tatsächlich vertrauen kann.

## Problem

LLMs formulieren sehr überzeugend, können aber auch falsche Zahlen oder unbelegte Erklärungen liefern.

Bei Datenanalysen ist das kritisch.

## Lösung

Unser System trennt deshalb:

1. Berechnung
2. sprachliche Erklärung
3. Verifikation

Die Zahlen werden von PySpark berechnet.

Das LLM erklärt die Ergebnisse.

Der Trust Guard prüft die zentrale Aussage gegen die echten Werte.

## Demo-Ablauf

1. Dashboard öffnen.
2. 1 Mio. Datensätze und KPIs zeigen.
3. Datenqualitäts-Tab zeigen.
4. KI-Assistent öffnen.
5. Frage stellen:
   "Wie hoch ist der Gesamtumsatz?"
6. LLM-Antwort zeigen.
7. Grünen Verifikationsstatus zeigen.
8. Erklären, dass eine falsche Zahl rot markiert würde.
9. Eine komplexe Warum-Frage zeigen und erklären, warum sie nicht automatisch verifizierbar ist.

## Kernaussage für die Prüfung

Ein LLM ist in diesem Projekt nicht die Quelle der Wahrheit.

Die Quelle der Wahrheit sind die deterministisch berechneten Daten.

Das LLM dient als sprachliche Schnittstelle.

Vertrauen entsteht erst durch die zusätzliche Prüfung.

## Technische Komponenten

- Python
- Apache Spark / PySpark
- Pandas für kleine Dashboard-Snapshots
- Streamlit
- Plotly
- OpenAI Responses API
- eigener Trust Guard

## Stärken

- große Datenmenge
- reproduzierbarer Datensatz
- strenge Datenbereinigung
- visuelle Demo
- LLM-Integration
- explizite Halluzinations-/Vertrauensprüfung
- automatisierte Tests

## Ehrliche Einschränkung

Nicht jede freie LLM-Antwort lässt sich automatisch beweisen.

Deshalb kennt das System drei Zustände:

- Grün: verifiziert
- Rot: widersprüchlich
- Gelb: nicht automatisch verifizierbar

Diese Unsicherheit wird bewusst sichtbar gemacht, statt sie zu verstecken.
