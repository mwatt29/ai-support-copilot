from typing import List, Tuple
from sqlalchemy import text
from apps.api.models import Ticket
from apps.api.ai_providers.local_provider import get_embeddings, get_completion

PROMPT_TEMPLATE = """You are a support agent. Use ONLY the sources below.
Cite sources inline like [S1], [S2]. If information is missing, say "I don't know based on the current knowledge base."

Ticket:
{ticket_text}

Sources:
{sources_block}

Answer concisely:
"""

def vector_search(db, org_id, query, k=3):
    [qvec] = get_embeddings([query])
    sql = text("""
        SELECT id, title, content, 1 - (embedding <=> :qvec) AS similarity
        FROM kb_articles
        WHERE org_id = :org_id
        ORDER BY embedding <=> :qvec
        LIMIT :k
    """)
    rows = db.execute(sql, {"qvec": str(qvec), "org_id": str(org_id), "k": k}).fetchall()
    return [{"id": str(r[0]), "title": r[1], "content": r[2], "similarity": float(r[3])} for r in rows]

def build_prompt(ticket_text: str, contexts: List[dict]) -> Tuple[str, list]:
    sources_block = []
    sources_meta = []
    for i, c in enumerate(contexts):
        sources_block.append(f"[S{i+1}] {c['title']}: {c['content'][:1200]}")
        sources_meta.append({"title": c["title"], "snippet": c["content"][:200]})
    prompt = PROMPT_TEMPLATE.format(ticket_text=ticket_text, sources_block="\n".join(sources_block))
    return prompt, sources_meta

def rag_suggest(db, ticket: Ticket):
    query = (ticket.subject or "") + "\n" + (ticket.body or "")
    contexts = vector_search(db, ticket.org_id, query, k=3)
    prompt, sources_meta = build_prompt(ticket.body or ticket.subject or "", contexts)
    answer = get_completion(prompt)
    return answer, sources_meta, "llama3"