import base64
from email.mime.text import MIMEText

from email_reader import get_gmail_service


def send_email_to_customer(to_address, subject, body):
    """
    Send an email to a customer using the Gmail account
    authenticated by email_reader.py.

    The customer email address is provided dynamically
    by main.py.
    """

    print("\n==========================================")
    print("SENDING EMAIL TO CUSTOMER")
    print("==========================================")

    print("To:", to_address)
    print("Subject:", subject)

    # --------------------------------------------------
    # STEP 1 — CONNECT TO GMAIL
    # --------------------------------------------------
    service = get_gmail_service()

    # --------------------------------------------------
    # STEP 2 — CREATE EMAIL
    # --------------------------------------------------
    message = MIMEText(body)

    message["To"] = to_address
    message["Subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    # --------------------------------------------------
    # STEP 3 — SEND THROUGH GMAIL API
    # --------------------------------------------------
    sent_message = service.users().messages().send(
        userId="me",
        body={
            "raw": raw_message
        }
    ).execute()

    print("Email sent successfully. Gmail message ID:")
    print(sent_message.get("id"))

    return sent_message