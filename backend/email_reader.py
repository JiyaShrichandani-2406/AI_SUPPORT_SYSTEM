
import os
import base64
import json
import uuid
import requests

from email.utils import parseaddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
PROCESSED_FILE = os.path.join(BASE_DIR, "processed_emails.json")

FASTAPI_URL = "http://127.0.0.1:8000/tickets"
FASTAPI_TIMEOUT = 240

SUPPORT_EMAIL = "support.team.demo@gmail.com"


# --------------------------------------------------
# CONNECT TO GMAIL
# --------------------------------------------------

def get_gmail_service():

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    elif not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Gmail credentials not found: {CREDENTIALS_FILE}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )

        creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    print("Successfully connected to Gmail!")

    return service


# --------------------------------------------------
# EMAIL HEADER HELPER
# --------------------------------------------------

def get_header(headers, name):

    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")

    return ""


# --------------------------------------------------
# DECODE EMAIL BODY
# --------------------------------------------------

def decode_body(data):

    if not data:
        return ""

    try:
        decoded = base64.urlsafe_b64decode(
            data.encode("UTF-8")
        )

        return decoded.decode("UTF-8", errors="replace")

    except Exception as error:
        print("Email body decoding error:", error)
        return ""


# --------------------------------------------------
# EXTRACT EMAIL BODY
# --------------------------------------------------

def extract_message_body(payload):

    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return decode_body(body_data)

    parts = payload.get("parts", [])

    for part in parts:

        result = extract_message_body(part)

        if result:
            return result

    if body_data:
        return decode_body(body_data)

    return ""


# --------------------------------------------------
# PROCESSED EMAIL MANAGEMENT
# --------------------------------------------------

def load_processed_ids():

    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return set(data)

    except (json.JSONDecodeError, OSError) as error:
        print("Could not read processed email file:", error)
        return set()


def save_processed_ids(processed_ids):

    with open(PROCESSED_FILE, "w", encoding="utf-8") as file:
        json.dump(
            sorted(list(processed_ids)),
            file,
            indent=4
        )


# --------------------------------------------------
# FILTER GOOGLE SECURITY EMAILS
# --------------------------------------------------

def is_google_security_email(sender, subject):

    sender_lower = sender.lower()
    subject_lower = subject.lower()

    google_domains = [
        "accounts.google.com",
        "google.com",
        "googlemail.com"
    ]

    security_keywords = [
        "security alert",
        "security notice",
        "new sign-in",
        "new device",
        "new device signed in",
        "suspicious sign-in",
        "suspicious activity",
        "password changed",
        "password reset",
        "2-step verification",
        "recovery email",
        "recovery phone",
        "critical security alert"
    ]

    is_google_sender = any(
        domain in sender_lower for domain in google_domains
    )

    is_security_subject = any(
        keyword in subject_lower for keyword in security_keywords
    )

    return is_google_sender and is_security_subject


# --------------------------------------------------
# FILTER AUTOMATED GOOGLE CLOUD ANNOUNCEMENTS
# --------------------------------------------------

def is_google_cloud_announcement(sender, subject):

    sender_lower = sender.lower()
    subject_lower = subject.lower()

    automated_google_senders = [
        "cloudplatform-noreply@google.com"
    ]

    announcement_keywords = [
        "oauth clients as agentic",
        "workspace mcp",
        "google cloud announcement"
    ]

    is_automated_sender = any(
        address in sender_lower
        for address in automated_google_senders
    )

    is_announcement = any(
        keyword in subject_lower
        for keyword in announcement_keywords
    )

    return is_automated_sender and is_announcement


# --------------------------------------------------
# FILTER DELIVERY FAILURE EMAILS
# --------------------------------------------------

def is_delivery_failure(sender, subject):

    sender_lower = sender.lower()
    subject_lower = subject.lower()

    delivery_failure_senders = [
        "mailer-daemon",
        "postmaster"
    ]

    delivery_failure_subjects = [
        "delivery status notification",
        "undelivered mail",
        "mail delivery failed",
        "delivery failure",
        "returned mail",
        "address not found"
    ]

    is_failure_sender = any(
        address in sender_lower
        for address in delivery_failure_senders
    )

    is_failure_subject = any(
        keyword in subject_lower
        for keyword in delivery_failure_subjects
    )

    return is_failure_sender or is_failure_subject


# --------------------------------------------------
# READ LATEST CUSTOMER EMAILS
# --------------------------------------------------

def read_latest_email(service):

    processed_ids = load_processed_ids()

    try:

        results = service.users().messages().list(
            userId="me",
            maxResults=10
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            print("No emails found.")
            return

        for message_item in messages:

            message_id = message_item["id"]

            if message_id in processed_ids:
                continue

            try:

                message = service.users().messages().get(
                    userId="me",
                    id=message_id,
                    format="full"
                ).execute()

                payload = message.get("payload", {})
                headers = payload.get("headers", [])

                sender_header = get_header(headers, "From")
                sender_name, sender_email = parseaddr(sender_header)

                sender = sender_header
                subject = get_header(headers, "Subject")
                received_at = get_header(headers, "Date")

                body = extract_message_body(payload)

                sender_lower = sender_email.lower()
                subject_lower = subject.lower()

                print("\n--------------------------------")
                print("Checking email:", subject)
                print("Sender:", sender)
                print("--------------------------------")

                # ----------------------------------
                # SKIP EMAILS SENT BY SUPPORT ACCOUNT
                # ----------------------------------

                if sender_lower == SUPPORT_EMAIL.lower():

                    print("Skipping outgoing support email.")

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    continue

                # ----------------------------------
                # SKIP GOOGLE SECURITY EMAILS
                # ----------------------------------

                if is_google_security_email(sender, subject):

                    print("Skipping Google security notification.")

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    continue

                # ----------------------------------
                # SKIP GOOGLE CLOUD ANNOUNCEMENTS
                # ----------------------------------

                if is_google_cloud_announcement(sender, subject):

                    print("Skipping automated Google Cloud announcement.")

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    continue

                # ----------------------------------
                # SKIP DELIVERY FAILURE EMAILS
                # ----------------------------------

                if is_delivery_failure(sender, subject):

                    print("Skipping email delivery failure notification.")

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    continue

                # ----------------------------------
                # SKIP EMPTY EMAILS
                # ----------------------------------

                if not sender_email or not subject or not body.strip():

                    print("Skipping email: missing sender, subject, or body.")

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    continue

                # ----------------------------------
                # CREATE TICKET
                # ----------------------------------

                ticket_id = "TKT-" + uuid.uuid4().hex[:8].upper()

                ticket_data = {
                    "ticket_id": ticket_id,
                    "sender": sender,
                    "subject": subject,
                    "message": body,
                    "received_at": received_at,
                    "gmail_message_id": message_id,
                    "status": "RECEIVED"
                }

                print("\nSending customer email to AI Support System...")
                print("Ticket ID:", ticket_id)

                # ----------------------------------
                # SEND EMAIL TO FASTAPI
                # ----------------------------------

                response = requests.post(
                    FASTAPI_URL,
                    json=ticket_data,
                    timeout=FASTAPI_TIMEOUT
                )

                response.raise_for_status()

                try:
                    response_data = response.json()
                except ValueError:
                    print("FastAPI returned an invalid JSON response.")
                    continue

                ticket_status = response_data.get("status", "").lower()

                # ----------------------------------
                # MARK ONLY SUCCESSFUL TICKETS
                # ----------------------------------

                if ticket_status in [
                    "success",
                    "partial",
                    "duplicate"
                ]:

                    print("Ticket processing result:", ticket_status)
                    print("Response:", response_data)

                    processed_ids.add(message_id)
                    save_processed_ids(processed_ids)

                    print("Email marked as processed.")

                else:

                    print(
                        "Ticket was not successfully processed. "
                        "Email will be retried."
                    )

                    print("FastAPI response:", response_data)

            except requests.exceptions.Timeout:

                print(
                    "FastAPI request timed out. "
                    "Email will remain unprocessed."
                )

            except requests.exceptions.RequestException as error:

                print("FastAPI request error:", error)

            except Exception as error:

                print("Error processing email:", error)

    except Exception as error:

        print("Gmail reading error:", error)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("Starting AI Support System Email Reader...")

    try:

        gmail_service = get_gmail_service()

        read_latest_email(gmail_service)

    except Exception as error:

        print("Email Reader Error:", error)
