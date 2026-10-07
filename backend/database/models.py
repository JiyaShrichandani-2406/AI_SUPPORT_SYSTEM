from sqlalchemy import Column, String, Text, ForeignKey
from database.database import Base


# ==========================================================
# SUPPORT TICKET
# ==========================================================

class SupportTicket(Base):

    __tablename__ = "support_tickets"

    ticket_id = Column(String, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    received_at = Column(String, nullable=True)
    gmail_message_id = Column(String, unique=True, nullable=False)
    status = Column(String, default="RECEIVED")


# ==========================================================
# AI TRIAGE + RAG RESULT
# ==========================================================

class AITriageResult(Base):

    __tablename__ = "ai_triage_results"

    triage_id = Column(String, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("support_tickets.ticket_id"), nullable=False)

    # AI triage fields (unchanged)
    summary = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    key_details = Column(Text, nullable=True)

    # RAG-generated draft (unchanged — this is the AI's first draft)
    ai_response = Column(Text, nullable=True)

    # ------------------------------------------------------
    # NEW: HUMAN REVIEW FIELDS
    # ------------------------------------------------------

    # PENDING_REVIEW -> APPROVED -> SENT   (or EDITED -> SENT)
    review_status = Column(String, default="PENDING_REVIEW")

    # The final text that actually gets emailed — starts as a
    # copy of ai_response, overwritten if a human edits it.
    final_response = Column(Text, nullable=True)

    # Timestamp set once the email is actually sent
    sent_at = Column(String, nullable=True)