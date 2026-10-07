import os

import base64

import json

import uuid

import requests



from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build





# ==========================================================

# GMAIL CONFIGURATION

# ==========================================================



SCOPES = [

    "https://www.googleapis.com/auth/gmail.readonly",

    "https://www.googleapis.com/auth/gmail.send"

]





# ==========================================================

# PROJECT PATHS

# ==========================================================



BASE_DIR = os.path.dirname(

    os.path.dirname(

        os.path.abspath(__file__)

    )

)





CREDENTIALS_FILE = os.path.join(

    BASE_DIR,

    "credentials.json"

)





TOKEN_FILE = os.path.join(

    BASE_DIR,

    "token.json"

)





PROCESSED_FILE = os.path.join(

    BASE_DIR,

    "processed_emails.json"

)





# ==========================================================

# FASTAPI CONFIGURATION

# ==========================================================



FASTAPI_URL = (

    "http://127.0.0.1:8000/tickets"

)





# IMPORTANT:

# RAG + Ollama can take longer than 10 seconds.

# 240 seconds gives FastAPI enough time to finish.

FASTAPI_TIMEOUT = 240





# ==========================================================

# SUPPORT MAILBOX

# ==========================================================



SUPPORT_EMAIL = (

    "support.team.demo@gmail.com"

)





# ==========================================================

# GMAIL SERVICE

# ==========================================================



def get_gmail_service():



    creds = None





    # ------------------------------------------------------

    # Load existing token

    # ------------------------------------------------------



    if os.path.exists(TOKEN_FILE):



        creds = Credentials.from_authorized_user_file(

            TOKEN_FILE,

            SCOPES

        )





    # ------------------------------------------------------

    # Refresh / create credentials

    # ------------------------------------------------------



    if not creds or not creds.valid:



        if (

            creds

            and creds.expired

            and creds.refresh_token

        ):



            creds.refresh(

                Request()

            )



        else:



            flow = (

                InstalledAppFlow

                .from_client_secrets_file(

                    CREDENTIALS_FILE,

                    SCOPES

                )

            )



            creds = flow.run_local_server(

                port=0,

                open_browser=True

            )





        # Save token



        with open(

            TOKEN_FILE,

            "w"

        ) as token:



            token.write(

                creds.to_json()

            )





    # ------------------------------------------------------

    # Build Gmail service

    # ------------------------------------------------------



    service = build(

        "gmail",

        "v1",

        credentials=creds

    )





    return service





# ==========================================================

# GET EMAIL HEADER

# ==========================================================



def get_header(

    headers,

    name

):



    for header in headers:



        if (

            header["name"].lower()

            == name.lower()

        ):



            return header["value"]





    return ""





# ==========================================================

# DECODE EMAIL BODY

# ==========================================================



def decode_body(data):



    decoded_data = (

        base64.urlsafe_b64decode(

            data.encode("UTF-8")

        )

    )





    return decoded_data.decode(

        "UTF-8",

        errors="replace"

    )





# ==========================================================

# EXTRACT EMAIL BODY

# ==========================================================



def extract_message_body(payload):



    # ------------------------------------------------------

    # Simple email

    # ------------------------------------------------------



    if payload.get(

        "body",

        {}

    ).get("data"):



        return decode_body(

            payload["body"]["data"]

        )





    # ------------------------------------------------------

    # Multipart email

    # ------------------------------------------------------



    parts = payload.get(

        "parts",

        []

    )





    for part in parts:



        mime_type = part.get(

            "mimeType",

            ""

        )





        # Plain text



        if mime_type == "text/plain":



            body_data = part.get(

                "body",

                {}

            ).get("data")





            if body_data:



                return decode_body(

                    body_data

                )





        # Nested multipart



        if part.get("parts"):



            body = extract_message_body(

                part

            )





            if body:



                return body





    return ""





# ==========================================================

# LOAD PROCESSED EMAIL IDS

# ==========================================================



def load_processed_ids():



    if not os.path.exists(

        PROCESSED_FILE

    ):



        return set()





    with open(

        PROCESSED_FILE,

        "r"

    ) as file:



        return set(

            json.load(file)

        )





# ==========================================================

# SAVE PROCESSED EMAIL IDS

# ==========================================================



def save_processed_ids(

    processed_ids

):



    with open(

        PROCESSED_FILE,

        "w"

    ) as file:



        json.dump(

            list(processed_ids),

            file,

            indent=4

        )





# ==========================================================

# READ LATEST EMAILS

# ==========================================================



def read_latest_email(

    service

):



    results = (

        service.users()

        .messages()

        .list(

            userId="me",

            maxResults=10

        )

        .execute()

    )





    messages = results.get(

        "messages",

        []

    )





    if not messages:



        print(

            "No emails found."

        )



        return





    processed_ids = (

        load_processed_ids()

    )





    # ======================================================

    # PROCESS EMAILS

    # ======================================================



    for message in messages:



        message_id = message["id"]





        # --------------------------------------------------

        # DUPLICATE GMAIL MESSAGE CHECK

        # --------------------------------------------------



        if message_id in processed_ids:



            continue





        # --------------------------------------------------

        # GET COMPLETE EMAIL

        # --------------------------------------------------



        email = (

            service.users()

            .messages()

            .get(

                userId="me",

                id=message_id,

                format="full"

            )

            .execute()

        )





        payload = email["payload"]





        headers = payload.get(

            "headers",

            []

        )





        # --------------------------------------------------

        # EXTRACT EMAIL INFORMATION

        # --------------------------------------------------



        sender = get_header(

            headers,

            "From"

        )





        subject = get_header(

            headers,

            "Subject"

        )





        received_at = get_header(

            headers,

            "Date"

        )





        body = extract_message_body(

            payload

        )





        # ==================================================

        # IGNORE EMAILS SENT BY SUPPORT SYSTEM

        # ==================================================

        #

        # This prevents the system from reading its own

        # outgoing support emails and creating tickets

        # from them.

        # ==================================================



        if (

            SUPPORT_EMAIL.lower()

            in sender.lower()

        ):



            print(

                "\nSkipping email sent "

                "from the support mailbox:"

            )



            print(

                sender

            )





            processed_ids.add(

                message_id

            )





            save_processed_ids(

                processed_ids

            )





            continue
        # ==================================================
        # IGNORE GOOGLE SECURITY EMAILS
        # ==================================================
        #
        # Google security/account notification emails should
        # NOT be converted into support tickets.
        #
        # We check both the sender and subject to avoid
        # accidentally treating security notifications as
        # customer support requests.
        # ==================================================

        google_security_senders = [
            "accounts.google.com",
            "google.com",
            "googlemail.com",
        ]

        google_security_subjects = [
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
            "2-step verification turned on",
            "2-step verification turned off",
            "recovery email",
            "recovery phone",
            "critical security alert",
        ]

        sender_lower = sender.lower()
        subject_lower = subject.lower()

        is_google_security_email = (
            any(
                domain in sender_lower
                for domain in google_security_senders
            )
            and any(
                keyword in subject_lower
                for keyword in google_security_subjects
            )
        )

        if is_google_security_email:

            print(
                "\nSkipping Google security email:"
            )

            print(
                "From:",
                sender
            )

            print(
                "Subject:",
                subject
            )

            # Mark it as processed so the same security email
            # is not checked again on the next run.
            processed_ids.add(
                message_id
            )

            save_processed_ids(
                processed_ids
            )

            continue







        # --------------------------------------------------

        # CREATE TICKET ID

        # --------------------------------------------------



        ticket_id = (

            "TKT-"

            + uuid.uuid4()

            .hex[:8]

            .upper()

        )





        # --------------------------------------------------

        # CREATE STRUCTURED TICKET

        # --------------------------------------------------



        ticket = {



            "ticket_id":

            ticket_id,



            "sender":

            sender,



            "subject":

            subject,



            "message":

            body,



            "received_at":

            received_at,



            "gmail_message_id":

            message_id,



            "status":

            "RECEIVED"

        }





        # ==================================================

        # DISPLAY STRUCTURED TICKET

        # ==================================================



        print(

            "\n========================================"

        )



        print(

            "EMAIL CONVERTED TO "

            "STRUCTURED TICKET"

        )



        print(

            "========================================"

        )





        print(

            json.dumps(

                ticket,

                indent=4

            )

        )





        print(

            "========================================"

        )





        # ==================================================

        # SEND TICKET TO FASTAPI

        # ==================================================



        try:



            print(

                "\nSending ticket to FastAPI..."

            )





            response = requests.post(



                FASTAPI_URL,



                json=ticket,



                timeout=FASTAPI_TIMEOUT

            )





            # ------------------------------------------------

            # SUCCESS

            # ------------------------------------------------



            if response.status_code == 200:



                print(

                    "\nTicket successfully "

                    "sent to FastAPI."

                )





                print(

                    "FastAPI response:"

                )





                try:



                    print(

                        json.dumps(

                            response.json(),

                            indent=4

                        )

                    )



                except ValueError:



                    print(

                        response.text

                    )





                # --------------------------------------------

                # Mark as processed ONLY after success

                # --------------------------------------------



                processed_ids.add(

                    message_id

                )





                save_processed_ids(

                    processed_ids

                )





            # ------------------------------------------------

            # FASTAPI ERROR

            # ------------------------------------------------



            else:



                print(

                    "\nFastAPI returned error:"

                )



                print(

                    response.status_code

                )



                print(

                    response.text

                )





        # ==================================================

        # CONNECTION / TIMEOUT ERROR

        # ==================================================



        except requests.exceptions.Timeout:



            print(

                "\nFastAPI request timed out."

            )



            print(

                "The ticket may still be "

                "processing in FastAPI."

            )



            print(

                "The Gmail message was NOT "

                "marked as processed."

            )





        except requests.exceptions.RequestException as error:



            print(

                "\nCould not connect to FastAPI:"

            )



            print(

                error

            )





# ==========================================================

# MAIN

# ==========================================================



if __name__ == "__main__":



    print(

        "Connecting to Gmail..."

    )





    service = get_gmail_service()





    print(

        "Successfully connected to Gmail!"

    )





    read_latest_email(

        service

    )