import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TIMESTAMP
from pgvector.sqlalchemy import Vector
from apps.api.db import Base

from pydantic import BaseModel

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    zendesk_subdomain = Column(String, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    external_id = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    customer_email = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class KBArticle(Base):
    __tablename__ = "kb_articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    source = Column(String)  # 'markdown', 'zendesk_help_center', etc.
    external_id = Column(String, nullable=True)
    title = Column(String)
    content = Column(Text)
    embedding = Column(Vector(1024)) 
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"))
    model = Column(String)
    answer = Column(Text)
    sources = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class AgentFeedback(Base):
    __tablename__ = "agent_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suggestion_id = Column(UUID(as_uuid=True), ForeignKey("suggestions.id"))
    used = Column(Boolean, default=False)
    edit_diff = Column(JSON, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# --- Pydantic Models ---
# Used for data validation in API endpoints

class TicketCreate(BaseModel):
    org: str
    subject: str
    body: str