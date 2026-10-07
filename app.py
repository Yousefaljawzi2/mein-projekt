import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.llm_assistant import answer_with_llm, llm_available
from src.trust_guard import reference_answer, verify_answer


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "dashboard_data"


@st.cache_data
def load_dashboard_data():
    with open(DATA_DIR / "summary.json", "r", encoding="utf-8") as handle:
        summary = json.load(handle)

    return {
        "summary": summary,
        "categories": pd.read_csv(DATA_DIR / "revenue_by_category.csv"),
        "countries": pd.read_csv(DATA_DIR / "revenue_by_country.csv"),
        "monthly": pd.read_csv(DATA_DIR / "monthly_revenue.csv"),
        "products": pd.read_csv(DATA_DIR / "top_products.csv"),
    }


def euro(value):
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def integer(value):
    return f"{int(value):,}".replace(",", ".")


st.set_page_config(
    page_title="Big Data Analytics Assistant",
    page_icon="📊",
    layout="wide",
)

data = load_dashboard_data()
summary = data["summary"]
kpis = summary["kpis"]
quality = summary["data_quality"]

st.title("📊 Big Data Analytics Assistant")
st.caption(
    "PySpark-Analyse von 1 Mio. E-Commerce-Zeilen + LLM-Fragen + automatische Vertrauensprüfung"
)

mode_text = "OpenAI LLM aktiv" if llm_available() else "Demo-Modus ohne API-Key"
st.sidebar.subheader("Systemstatus")
st.sidebar.write(f"**Modus:** {mode_text}")
st.sidebar.write(f"**Datenqualität:** {quality['quality_rate_pct']:.2f} %")
st.sidebar.write(f"**Gültige Zeilen:** {integer(quality['valid_rows'])}")
st.sidebar.info(
    "Für den echten LLM-Modus OPENAI_API_KEY setzen. Ohne Key bleibt die Demo vollständig bedienbar und nutzt überprüfbare Referenzantworten."
)

tab_dashboard, tab_ai, tab_quality, tab_method = st.tabs(
    ["Dashboard", "KI-Assistent", "Datenqualität", "Methodik"]
)

with tab_dashboard:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bestellungen", integer(kpis["total_orders"]))
    c2.metric("Kunden", integer(kpis["unique_customers"]))
    c3.metric("Gesamtumsatz", euro(kpis["total_revenue"]))
    c4.metric("Ø Umsatz / Bestellung", euro(kpis["average_order_revenue"]))

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            data["categories"],
            x="category",
            y="revenue",
            text_auto=".3s",
            title="Umsatz nach Kategorie",
            labels={"category": "Kategorie", "revenue": "Umsatz (€)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            data["countries"],
            x="country",
            y="revenue",
            text_auto=".3s",
            title="Umsatz nach Land",
            labels={"country": "Land", "revenue": "Umsatz (€)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        data["monthly"],
        x="month",
        y="revenue",
        markers=True,
        title="Monatlicher Umsatzverlauf",
        labels={"month": "Monat", "revenue": "Umsatz (€)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    top10 = data["products"].head(10).sort_values("revenue")
    fig = px.bar(
        top10,
        x="revenue",
        y="product",
        orientation="h",
        text_auto=".3s",
        title="Top 10 Produkte nach Umsatz",
        labels={"product": "Produkt", "revenue": "Umsatz (€)"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab_ai:
    st.subheader("Frag die Daten")
    st.write(
        "Der Assistent bekommt nur aggregierte, geprüfte Fakten aus der Big-Data-Pipeline. "
        "Danach kontrolliert der Trust Guard die Antwort noch einmal gegen Referenzwerte."
    )

    examples = [
        "Wie hoch ist der Gesamtumsatz?",
        "Welches Produkt erzielt den höchsten Umsatz?",
        "Welches Land hat den höchsten Umsatz?",
        "Welche Kategorie ist am stärksten?",
        "Welcher Monat war am stärksten?",
        "Wie viele Ausreißer wurden erkannt?",
        "Wie viele eindeutige Kunden gibt es?",
    ]
    selected = st.selectbox("Beispielfrage", examples)
    question = st.text_input("Eigene Frage", value=selected)

    if st.button("Analysieren", type="primary"):
        if not question.strip():
            st.warning("Bitte eine Frage eingeben.")
        else:
            with st.spinner("Antwort wird erzeugt und überprüft ..."):
                if llm_available():
                    try:
                        answer = answer_with_llm(question, data)
                        source = "OpenAI LLM"
                    except Exception as exc:
                        answer = reference_answer(question, data)
                        source = "Fallback nach LLM-Fehler"
                        st.warning(f"LLM-Aufruf fehlgeschlagen: {exc}")
                else:
                    answer = reference_answer(question, data)
                    source = "Verifizierbarer Demo-Modus"

                verification = verify_answer(question, answer, data)

            st.markdown("### Antwort")
            st.write(answer)
            st.caption(f"Antwortquelle: {source}")

            st.markdown("### Trust Guard")
            status = verification["status"]
            if status == "verified":
                st.success("🟢 Verifiziert: Die zentrale Aussage stimmt mit den berechneten Daten überein.")
            elif status == "failed":
                st.error("🔴 Nicht verifiziert: Die Antwort widerspricht dem erwarteten Referenzwert.")
            else:
                st.warning("🟡 Nicht automatisch verifizierbar: Für diese Frage gibt es noch keine feste Prüfregel.")

            with st.expander("Prüfdetails"):
                st.json(verification)

with tab_quality:
    st.subheader("Datenqualität")
    q1, q2, q3 = st.columns(3)
    q1.metric("Eingelesen", integer(quality["input_rows"]))
    q2.metric("Gültig", integer(quality["valid_rows"]))
    q3.metric("Abgelehnt", integer(quality["rejected_rows"]))

    st.progress(quality["quality_rate_pct"] / 100)
    st.write(f"**Qualitätsquote:** {quality['quality_rate_pct']:.2f} %")

    st.markdown(
        """
        Die Pipeline prüft unter anderem:
        - fehlende Pflichtwerte,
        - ID-Formate und doppelte Bestell-IDs,
        - Produkt-/Kategorie-Konsistenz,
        - erlaubte Länder,
        - plausible Mengen und Preise,
        - gültige Zeitstempel und Zeitraum.
        """
    )

    st.info(
        "Der aktuelle Datensatz wurde synthetisch kontrolliert erzeugt und erfüllt alle Regeln. "
        "Die Bereinigung ist trotzdem so implementiert, dass fehlerhafte reale Daten separat abgelehnt und dokumentiert werden."
    )

with tab_method:
    st.subheader("Warum kann man der Antwort vertrauen?")
    st.markdown(
        """
        **1. Big Data Layer:** PySpark liest und validiert den vollständigen Datensatz.

        **2. Analytics Layer:** Kennzahlen und Aggregationen werden deterministisch berechnet.

        **3. LLM Layer:** Das Sprachmodell erhält nur die bereits berechneten Fakten und darf keine neuen Zahlen erfinden.

        **4. Trust Guard:** Für zentrale Prüfungsfragen wird die LLM-Antwort automatisch gegen Referenzwerte kontrolliert.

        **5. Transparenz:** Wenn eine Frage nicht automatisch verifizierbar ist, wird das sichtbar als gelber Status angezeigt.
        """
    )

    st.code(
        "spark-submit src/analytics.py --input data/sales_1m.csv --output output",
        language="bash",
    )
    st.code("streamlit run app.py", language="bash")
