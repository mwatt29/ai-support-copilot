import argparse, os, glob
from sqlalchemy.orm import Session
from apps.api.db import SessionLocal
from apps.api.models import KBArticle
from apps.api.ai_providers.local_provider import get_embeddings
from apps.api.utils import get_or_create_org

def load_markdown_files(path: str):
    files = glob.glob(os.path.join(path, "*.md"))
    docs = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            docs.append((os.path.basename(f), fh.read()))
    return docs

def chunk(text: str, max_tokens=700, overlap_tokens=120):
    chars = 4 * max_tokens
    ovlp = 4 * overlap_tokens
    out = []
    i = 0
    while i < len(text):
        out.append(text[i:i+chars])
        i += chars - ovlp
    return out

def main(org_name: str, path: str):
    db: Session = SessionLocal()
    try:
        org = get_or_create_org(db, org_name)
        docs = load_markdown_files(path)
        total_parts = 0
        for title, content in docs:
            parts = chunk(content)
            embeddings = get_embeddings(parts)
            total_parts += len(parts)
            for idx, (part, emb) in enumerate(zip(parts, embeddings)):
                art = KBArticle(
                    org_id=org.id,
                    source="markdown",
                    external_id=f"{title}#chunk-{idx}",
                    title=title if idx == 0 else f"{title} (part {idx+1})",
                    content=part,
                    embedding=emb,
                )
                db.add(art)
        db.commit()
        print(f"Ingested {len(docs)} docs with {total_parts} chunks into org '{org_name}'")
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--org", required=True, help="Organization name (tenant)")
    p.add_argument("--path", required=True, help="Path to folder with .md files")
    args = p.parse_args()
    main(args.org, args.path)
