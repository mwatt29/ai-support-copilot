import os
from typing import List
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-large"
GEN_MODEL = "gpt-4o-mini"  # cost-effective for MVP

def embed_texts(texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def generate_answer(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=GEN_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise, accurate support assistant. If the answer is not in the provided context, say you don't know."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
