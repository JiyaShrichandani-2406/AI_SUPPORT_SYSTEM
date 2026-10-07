from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from email_sender import send_email_to_customer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Literal
import json
import uuid


# ==========================================================
# PROJECT IMPORTS
# ==========================================================

from models import Ticket

from ai_module.triage import analyze_ticket

from rag.rag_generator import generate_rag_response

from database.database import get_db

from database.models import (
    SupportTicket,
    AITriageResult
)


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title="AI Technical Support System"
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ==========================================================
# STATUS UPDATE MODEL
# ==========================================================

class StatusUpdate(BaseModel):

    status: Literal[
        "RECEIVED",
        "TRIAGED",
        "IN_PROGRESS",
        "RESOLVED"
    ]


# ==========================================================
# HOME
# ==========================================================

@app.get("/")
def home():

    return {
        "message":
        "AI Technical Support System is running"
    }


# ==========================================================
# RECEIVE SUPPORT TICKET
# ==========================================================

@app.post("/tickets")
def receive_ticket(
    ticket: Ticket,
    db: Session = Depends(get_db)
):

    print("\n==========================================")
    print("TICKET RECEIVED")
    print("==========================================")

    print("Ticket ID:", ticket.ticket_id)
    print("Sender:", ticket.sender)
    print("Subject:", ticket.subject)
    print("Message:", ticket.message)
    print("Received At:", ticket.received_at)
    print(
        "Gmail Message ID:",
        ticket.gmail_message_id
    )
    print("Status:", ticket.status)


    # ======================================================
    # STEP 1 — DUPLICATE CHECK
    # ======================================================
    #
    # IMPORTANT:
    # Check duplicate BEFORE AI/RAG processing.
    # This prevents the same Gmail message from being
    # analyzed multiple times.
    # ======================================================

    existing_ticket = db.query(
        SupportTicket
    ).filter(
        SupportTicket.gmail_message_id
        == ticket.gmail_message_id
    ).first()


    if existing_ticket:

        print("\n==========================================")
        print("DUPLICATE TICKET")
        print("==========================================")

        print(
            "This Gmail message has already "
            "been processed."
        )

        print(
            "Existing Ticket ID:",
            existing_ticket.ticket_id
        )

        return {
            "status": "duplicate",

            "message":
            "This ticket has already been processed.",

            "ticket_id":
            existing_ticket.ticket_id
        }


    # ======================================================
    # STEP 2 — AI TRIAGE
    # ======================================================

    print("\n==========================================")
    print("AI TRIAGE")
    print("==========================================")

    print("Sending ticket to AI...\n")


    try:

        ai_result = analyze_ticket(
            ticket.subject or "",
            ticket.message
        )

    except Exception as error:

        print("\nAI TRIAGE ERROR:")
        print(error)

        return {
            "status": "error",

            "message":
            "AI could not analyze the ticket.",

            "error": str(error)
        }


    if ai_result is None:

        return {
            "status": "error",

            "message":
            "AI could not analyze the ticket."
        }


    print("\n==========================================")
    print("AI TRIAGE RESULT")
    print("==========================================")


    print(
        json.dumps(
            ai_result,
            indent=4
        )
    )


    # ======================================================
    # STEP 3 — BUILD COMPLETE TICKET FOR RAG
    # ======================================================

    rag_ticket_text = f"""
Subject: {ticket.subject or ""}

Customer Message:
{ticket.message}
"""


    print("\n==========================================")
    print("RAG GENERATION")
    print("==========================================")

    print(
        "Sending customer ticket to RAG..."
    )


    # ======================================================
    # STEP 4 — RAG + OLLAMA
    # ======================================================

    rag_result = {
        "response": None,
        "sources": []
    }


    try:

        rag_result = generate_rag_response(
            ticket_text=rag_ticket_text,
            top_k=2
        )

    except Exception as error:

        print("\nRAG ERROR:")
        print(error)

        rag_result = {
            "response": None,
            "sources": []
        }


    # ======================================================
    # STEP 5 — EXTRACT RAG RESPONSE
    # ======================================================

    ai_response = None
    rag_sources = []


    if isinstance(
        rag_result,
        dict
    ):

        ai_response = rag_result.get(
            "response"
        )

        rag_sources = rag_result.get(
            "sources",
            []
        )


    elif isinstance(
        rag_result,
        str
    ):

        ai_response = rag_result


    # ======================================================
    # DISPLAY CLIENT RESPONSE
    # ======================================================

    print("\n==========================================")
    print("CLIENT-READY AI RESPONSE")
    print("==========================================")


    if ai_response:

        print(ai_response)

    else:

        print(
            "The AI response could not be generated "
            "within the allowed time."
        )


    # ======================================================
    # STEP 6 — SAVE INCOMING TICKET
    # ======================================================

    new_ticket = SupportTicket(

        ticket_id=ticket.ticket_id,

        sender=ticket.sender,

        subject=ticket.subject,

        message=ticket.message,

        received_at=ticket.received_at,

        gmail_message_id=ticket.gmail_message_id,

        status="TRIAGED"
    )


    db.add(new_ticket)


    # ======================================================
    # STEP 7 — SAVE AI TRIAGE + RAG RESPONSE
    # ======================================================

    new_triage = AITriageResult(

        triage_id=
        "TRI-" +
        uuid.uuid4().hex[:8].upper(),

        ticket_id=ticket.ticket_id,

        summary=
        ai_result.get("summary"),

        category=
        ai_result.get("category"),

        intent=
        ai_result.get("intent"),

        urgency=
        ai_result.get("urgency"),

        sentiment=
        ai_result.get("sentiment"),

        key_details=
        json.dumps(
            ai_result.get(
                "key_details",
                []
            )
        ),

        ai_response=ai_response
    )


    db.add(new_triage)

# ==========================================================
# APPROVE AND SEND RESPONSE TO CUSTOMER
# ==========================================================

@app.post("/tickets/{ticket_id}/approve")
def approve_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):

    print("\n==========================================")
    print("APPROVING TICKET")
    print("==========================================")
    print("Ticket ID:", ticket_id)

    # ------------------------------------------------------
    # Find ticket
    # ------------------------------------------------------

    ticket = db.query(
        SupportTicket
    ).filter(
        SupportTicket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {
            "status": "error",
            "message": "Ticket not found"
        }

    # ------------------------------------------------------
    # Find AI response
    # ------------------------------------------------------

    ai_result = db.query(
        AITriageResult
    ).filter(
        AITriageResult.ticket_id == ticket_id
    ).first()

    if not ai_result:
        return {
            "status": "error",
            "message": "AI response not found"
        }

    if not ai_result.ai_response:
        return {
            "status": "error",
            "message": "No customer response is available to send"
        }

    # ------------------------------------------------------
    # Extract customer email
    #
    # Example:
    # Jiya Shrichandani <jiyashrichandani6@gmail.com>
    # ------------------------------------------------------

    sender = ticket.sender or ""

    if "<" in sender and ">" in sender:
        customer_email = sender.split("<")[1].split(">")[0].strip()
    else:
        customer_email = sender.strip()

    if not customer_email or "@" not in customer_email:
        return {
            "status": "error",
            "message": "Could not determine customer email address"
        }

    print("Customer Email:", customer_email)

    # ------------------------------------------------------
    # Build subject
    # ------------------------------------------------------

    subject = ticket.subject or "Support Response"

    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject

    # ------------------------------------------------------
    # SEND EMAIL
    # ------------------------------------------------------

    try:

        sent_message = send_email_to_customer(
            to_address=customer_email,
            subject=subject,
            body=ai_result.ai_response
        )

    except Exception as error:

        print("\nEMAIL SEND ERROR:")
        print(error)

        return {
            "status": "error",
            "message": "Failed to send email to customer",
            "error": str(error)
        }

    # ------------------------------------------------------
    # Update ticket status
    # ------------------------------------------------------

    try:

        ticket.status = "RESOLVED"

        db.commit()
        db.refresh(ticket)

    except Exception as error:

        db.rollback()

        return {
            "status": "error",
            "message": "Email was sent, but ticket status could not be updated",
            "error": str(error)
        }

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print("\n==========================================")
    print("CUSTOMER EMAIL SENT SUCCESSFULLY")
    print("==========================================")
    print("To:", customer_email)
    print("Ticket ID:", ticket_id)
    print("Gmail Message ID:", sent_message.get("id"))

    return {
        "status": "success",
        "message": "Response sent successfully to customer.",
        "ticket_id": ticket_id,
        "customer_email": customer_email,
        "gmail_message_id": sent_message.get("id"),
        "ticket_status": ticket.status
    }

    # ======================================================
    # STEP 8 — SAVE EVERYTHING TO DATABASE
    # ======================================================

    try:

        db.commit()


        print("\n==========================================")
        print("DATABASE")
        print("==========================================")

        print(
            "Ticket saved successfully."
        )

        print(
            "AI triage saved successfully."
        )


        if ai_response:

            print(
                "RAG client response "
                "saved successfully."
            )

        else:

            print(
                "RAG response was not generated."
            )


    except Exception as error:

        db.rollback()

        print("\nDATABASE ERROR:")
        print(error)

        return {
            "status": "error",

            "message":
            "Could not save ticket and AI response "
            "to database.",

            "error": str(error)
        }


    # ======================================================
    # STEP 9 — FINAL API RESPONSE
    # ======================================================

    if ai_response:

        return {

            "status": "success",

            "message":
            "Ticket analyzed, RAG response generated "
            "and saved successfully. Awaiting human review.",

            "ticket_id":
            ticket.ticket_id,

            "ai_analysis":
            ai_result,

            "client_response":
            ai_response,

            "rag_sources":
            rag_sources
        }


    else:

        return {

            "status": "partial",

            "message":
            "Ticket received and AI triage was saved, "
            "but the customer response could not be generated.",

            "ticket_id":
            ticket.ticket_id,

            "ai_analysis":
            ai_result,

            "client_response":
            "",

            "rag_sources":
            rag_sources
        }


# ==========================================================
# GET ALL TICKETS
# ==========================================================

@app.get("/tickets")
def get_all_tickets(
    db: Session = Depends(get_db)
):

    tickets = db.query(
        SupportTicket
    ).all()

    return tickets


# ==========================================================
# GET ONE TICKET
# ==========================================================

@app.get("/tickets/{ticket_id}")
def get_ticket(

    ticket_id: str,

    db: Session = Depends(get_db)
):

    # ------------------------------------------------------
    # Find ticket
    # ------------------------------------------------------

    ticket = db.query(

        SupportTicket

    ).filter(

        SupportTicket.ticket_id
        == ticket_id

    ).first()


    if not ticket:

        return {

            "status": "error",

            "message":
            "Ticket not found"
        }


    # ------------------------------------------------------
    # Find AI result
    # ------------------------------------------------------

    ai_result = db.query(

        AITriageResult

    ).filter(

        AITriageResult.ticket_id
        == ticket_id

    ).first()


    # ------------------------------------------------------
    # Prepare AI analysis
    # ------------------------------------------------------

    ai_analysis = None


    if ai_result:

        key_details = []


        try:

            key_details = json.loads(
                ai_result.key_details
            )

        except (
            TypeError,
            json.JSONDecodeError
        ):

            key_details = (
                ai_result.key_details
            )


        ai_analysis = {

            "triage_id":
            ai_result.triage_id,

            "summary":
            ai_result.summary,

            "category":
            ai_result.category,

            "intent":
            ai_result.intent,

            "urgency":
            ai_result.urgency,

            "sentiment":
            ai_result.sentiment,

            "key_details":
            key_details,

            "ai_response":
            ai_result.ai_response
        }


    # ------------------------------------------------------
    # Return complete ticket
    # ------------------------------------------------------

    return {

        "ticket": {

            "ticket_id":
            ticket.ticket_id,

            "sender":
            ticket.sender,

            "subject":
            ticket.subject,

            "message":
            ticket.message,

            "received_at":
            ticket.received_at,

            "gmail_message_id":
            ticket.gmail_message_id,

            "status":
            ticket.status
        },

        "ai_analysis":
        ai_analysis
    }


# ==========================================================
# UPDATE TICKET STATUS
# ==========================================================

@app.put("/tickets/{ticket_id}")
def update_ticket_status(

    ticket_id: str,

    status_update: StatusUpdate,

    db: Session = Depends(get_db)
):

    # ------------------------------------------------------
    # Find ticket
    # ------------------------------------------------------

    ticket = db.query(

        SupportTicket

    ).filter(

        SupportTicket.ticket_id
        == ticket_id

    ).first()


    if not ticket:

        return {

            "status": "error",

            "message":
            "Ticket not found"
        }


    # ------------------------------------------------------
    # Update status
    # ------------------------------------------------------

    ticket.status = (
        status_update.status
    )


    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    try:

        db.commit()

        db.refresh(ticket)

    except Exception as error:

        db.rollback()

        return {

            "status": "error",

            "message":
            "Could not update ticket",

            "error":
            str(error)
        }


    # ------------------------------------------------------
    # Return updated ticket
    # ------------------------------------------------------

    return {

        "status": "success",

        "message":
        "Ticket status updated successfully.",

        "ticket": {

            "ticket_id":
            ticket.ticket_id,

            "sender":
            ticket.sender,

            "subject":
            ticket.subject,

            "status":
            ticket.status
        }
    }