import argparse, uuid
from sqlalchemy.orm import Session
from apps.api.db import SessionLocal
from apps.api.models import Ticket
from apps.api.utils import get_or_create_org

def main(org_name: str, subject: str, body: str, requester: str = "customer@example.com"):
    db: Session = SessionLocal()
    try:
        org = get_or_create_org(db, org_name)
        t = Ticket(org_id=org.id, external_id=str(uuid.uuid4()), subject=subject, body=body, customer_email=requester)
        db.add(t); db.commit(); db.refresh(t)
        print({"ticket_id": str(t.id), "org_id": str(org.id)})
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--org", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--requester", default="customer@example.com")
    args = p.parse_args()
    main(args.org, args.subject, args.body, args.requester)
