import json
import os

from openai import OpenAI


SYSTEM_INSTRUCTIONS = """
Du bist ein Datenanalyse-Assistent für ein Hochschulprojekt.
Antworte ausschließlich auf Basis der bereitgestellten, bereits berechneten Fakten.
Erfinde keine Kennzahlen, Ursachen oder Zusammenhänge.
Wenn die Daten eine Frage nicht beantworten, sage klar: "Nicht durch die vorliegenden Daten belegt."
Verwende bei Geldbeträgen möglichst den exakten Wert aus dem Kontext.
Antworte auf Deutsch, knapp und verständlich.
"""


def llm_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _context_payload(data: dict) -> dict:
    summary = data["summary"]

    return {
        "summary": summary,
        "revenue_by_category": data["categories"].to_dict(orient="records"),
        "revenue_by_country": data["countries"].to_dict(orient="records"),
        "monthly_revenue": data["monthly"].to_dict(orient="records"),
        "top_products": data["products"].head(12).to_dict(orient="records"),
    }


def answer_with_llm(question: str, data: dict) -> str:
    if not llm_available():
        raise RuntimeError("OPENAI_API_KEY ist nicht gesetzt.")

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
    context = json.dumps(_context_payload(data), ensure_ascii=False)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": (
                    "Geprüfte Datenbasis:\n"
                    f"{context}\n\n"
                    f"Frage: {question}"
                ),
            },
        ],
    )

    return response.output_text.strip()
