import uuid
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, HTTPException, Query, Depends 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from apps.api.db import Base, engine, SessionLocal, get_db
from apps.api.models import Ticket, Suggestion, AgentFeedback, TicketCreate 
from apps.api.rag import rag_suggest
from apps.api.utils import get_or_create_org

import apps.api.models  # noqa: F401

app = FastAPI(title="AI Support Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

class SuggestionRequest(BaseModel):
    ticketId: str

class SuggestionResponse(BaseModel):
    answer: str
    sources: list
    model: str
    suggestionId: str

class FeedbackRequest(BaseModel):
    suggestionId: str
    used: bool
    editDiff: dict | None = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/webhooks/zendesk")
async def zendesk_webhook(req: Request):
    payload = await req.json()
    org_name = payload.get("org", "Acme Inc")
    ticket = payload.get("ticket", {})
    subject = ticket.get("subject", "")
    body = ticket.get("body", "")
    requester = ticket.get("requester", "")
    external_id = str(ticket.get("id") or uuid.uuid4())

    db = SessionLocal()
    try:
        org = get_or_create_org(db, org_name)
        t = Ticket(
            org_id=org.id,
            external_id=external_id,
            subject=subject,
            body=body,
            customer_email=requester,
        )
        db.add(t); db.commit(); db.refresh(t)
        return {"ok": True, "ticket_id": str(t.id)}
    finally:
        db.close()

@app.get("/lookup-ticket")
def lookup_ticket(externalId: str = Query(...)):
    db = SessionLocal()
    try:
        t = db.execute(select(Ticket).where(Ticket.external_id == externalId).order_by(Ticket.created_at.desc())).scalars().first()
        if not t:
            return {"ticket_uuid": None}
        return {"ticket_uuid": str(t.id)}
    finally:
        db.close()

@app.post("/suggest", response_model=SuggestionResponse)
def suggest(req: SuggestionRequest):
    db = SessionLocal()
    try:
        ticket = db.get(Ticket, uuid.UUID(req.ticketId))
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        answer, sources, model = rag_suggest(db, ticket)
        s = Suggestion(ticket_id=ticket.id, answer=answer, sources=sources, model=model)
        db.add(s); db.commit(); db.refresh(s)
        return SuggestionResponse(answer=answer, sources=sources, model=model, suggestionId=str(s.id))
    finally:
        db.close()

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    db = SessionLocal()
    try:
        suggestion = db.get(Suggestion, uuid.UUID(req.suggestionId))
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        fb = AgentFeedback(suggestion_id=suggestion.id, used=req.used, edit_diff=req.editDiff or {})
        db.add(fb); db.commit()
        return {"ok": True}
    finally:
        db.close()

       
@app.post("/create_simple_ticket", status_code=201)
def create_simple_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    """A simple endpoint for the web UI to create a ticket and get an ID."""
    org = get_or_create_org(db, ticket_data.org)
    new_ticket = Ticket(
        org_id=org.id,
        subject=ticket_data.subject,
        body=ticket_data.body
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return {"ticketId": new_ticket.id}
