from pydantic import BaseModel
from typing import List

class Ticket(BaseModel):
    ticket_id: str
    sender: str
    subject: str
    message: str
    received_at: str
    gmail_message_id: str
    status: str


class TriageResult(BaseModel):
    summary: str
    category: str
    intent: str
    urgency: str
    sentiment: str
    key_details: List[str]