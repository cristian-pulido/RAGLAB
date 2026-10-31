"""Envía una pregunta breve a un modelo de OpenRouter desde el entorno RAGLAB."""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise SystemExit(
        "No se encontró OPENAI_API_KEY. Guarda tu clave de OpenRouter en el .env de la raíz."
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    messages=[
        {
            "role": "user",
            "content": "Explica en una frase qué es un sistema RAG, para alguien que empieza.",
        }
    ],
    max_tokens=120,
)

print(response.choices[0].message.content)
