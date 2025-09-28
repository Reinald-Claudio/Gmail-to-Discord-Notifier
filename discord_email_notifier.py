from __future__ import print_function
import os
import os.path
import base64
import re
import time
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# Load values from my .env
load_dotenv()
webhook_url = os.getenv("DISCORD_WEBHOOK")

# If modifying these scopes, delete token.json
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# === Gmail setup === #
def gmail_authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

# --- Fetching unread emails --- #
def get_unread_emails(service, max_results=5):
    results = service.users().messages().list(userId="me", labelIds=["UNREAD"], maxResults=max_results).execute()
    messages = results.get("messages", [])
    email_list = []

    for msg in messages:
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = txt.get("payload", {})
        headers = payload.get("headers", [])
        subject = None
        for d in headers:
            if d.get("name") == "Subject":
                subject = d.get("value")
                break
        snippet = txt.get("snippet", "")
        email_list.append((msg["id"], subject, snippet))
    return email_list

# Storing IDs in a JSON file
SENT_FILE = "sent_ids.json"

def load_sent_ids():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_ids(sent_ids):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_ids), f)

# === Discord === #
def send_to_discord(subject, snippet):
    if not webhook_url:
        print("ERROR: Discord webhook not configured. Set DISCORD_WEBHOOK in .env")
        return
    data = {"content": f"📧 **New Email**\n**Subject:** {subject}\n**Snippet:** {snippet}"}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:  # 204 = Discord success (no content)
            print("Discord webhook failed:", response.status_code, response.text[:200])
    except Exception as e:
        print("Error sending to Discord:", e)

if __name__ == "__main__":
    # checking for webhook
    if not webhook_url:
        raise SystemExit("Missing DISCORD_WEBHOOK in .env")

    service = gmail_authenticate()
    sent_ids = load_sent_ids()
    print("Discord Email Notifier running.. (Ctrl+C to stop)")

    while True:
        unread_emails = get_unread_emails(service)
        if not unread_emails:
            print("No new emails.")
        else:
            for msg_id, subject, snippet in unread_emails:
                if msg_id not in sent_ids:
                    print(f"{subject} - {snippet}")
                    send_to_discord(subject, snippet)
                    sent_ids.add(msg_id)
                    save_sent_ids(sent_ids)
        time.sleep(60)
