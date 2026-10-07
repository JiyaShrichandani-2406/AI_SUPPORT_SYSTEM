import base64
from email.mime.text import MIMEText

from email_reader import get_gmail_service


def send_email_to_customer(to_address, subject, body):

    print("\n==========================================")
    print("SENDING EMAIL TO CUSTOMER")
    print("==========================================")

    print("To:", to_address)
    print("Subject:", subject)


    # ======================================================
    # STEP 1 — CONNECT TO GMAIL (reuses reader's auth/token)
    # ======================================================

    service = get_gmail_service()


    # ======================================================
    # STEP 2 — BUILD THE EMAIL MESSAGE
    # ======================================================

    message = MIMEText(body)

    message["to"] = to_address
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")


    # ======================================================
    # STEP 3 — SEND VIA GMAIL API
    # ======================================================

    sent_message = service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    print("Email sent successfully. Gmail message ID:")
    print(sent_message.get("id"))

    return sent_message


# ==========================================================
# MANUAL SEND TEST
# ==========================================================

if __name__ == "__main__":

    send_email_to_customer(
        to_address="test@example.com",
        subject="Test email from AI Support System",
        body="This is a test of the send_email_to_customer function."
    )