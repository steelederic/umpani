import os
import time
import json
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def get_credentials():
    """
    Get the user's Google API credentials or refresh them if necessary.

    This function reads the 'credentials.json' file, which contains the OAuth 2.0 client ID and secret.
    If the tokens are not found, expired, or invalid, it opens a browser window for user authentication and
    obtains new tokens.

    Returns:
        creds (google.oauth2.credentials.Credentials): The user's Google API credentials.
    """
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = Credentials.from_authorized_user_file("token.pickle", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            token.write(creds.to_json().encode())

    return creds


def monitor_inbox_for_subject(subject, service):
    """
    Monitor the user's Gmail inbox for new messages with subjects starting with the specified string.

    This function searches the user's Gmail inbox for unread messages with subjects starting with the specified string.
    It then marks the found messages as read and appends their subjects along with timestamps to the 'results.json' file.
    """

    query = f'subject:"{subject}" is:unread'
    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    unique_subjects = set()

    if not messages:
        print("No new messages found.")
    else:
        for message in messages:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=["subject"],
                )
                .execute()
            )
            subject_value = msg["payload"]["headers"][0]["value"]

            if subject_value.startswith(subject):
                unique_subjects.add(subject_value)

                # Mark the message as read
                service.users().messages().modify(
                    userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}
                ).execute()

        if unique_subjects:
            print(
                f'Found {len(unique_subjects)} new messages with subject starting with "{subject}":'
            )
            results_data = []
            for subject in unique_subjects:
                print(subject)
                now = datetime.now(pytz.utc).astimezone(pytz.timezone("US/Eastern"))
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
                results_data.append({"subject": subject, "timestamp": timestamp})

            if os.path.exists('results.json'):
                with open('results.json', 'r') as file:
                    file_content = file.read()
                    existing_subjects = json.loads(file_content) if file_content else []
            else:
                existing_subjects = []

            updated_subjects = existing_subjects + results_data

            with open("results.json", "w") as file:
                json.dump(updated_subjects, file, indent=2)

        else:
            print(f'No new messages found with subject starting with "{subject}".')


def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    subject_to_search = os.getenv("SUBJECT_TO_SEARCH")

    while True:
        print(f"Checking for emails with subject '{subject_to_search}'...")
        monitor_inbox_for_subject(subject_to_search, service)
        time.sleep(int(os.getenv("POLLING_INTERVAL")))


if __name__ == "__main__":
    main()
