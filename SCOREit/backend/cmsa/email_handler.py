import base64
import csv
import os
import pickle
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate the user using OAuth 2.0 and return the credentials."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\Designuser\Desktop\SCOREit\scripts\credentials.json',  # Path to your credentials.json
                SCOPES
            )
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_email(creds, team_name, recipient_email):
    """Send an email using the Gmail API."""
    # Create the email content
    subject = 'Game Score Submission'
    body = f"Dear Coach, please submit your score for {team_name}."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'scoreit.report@gmail.com'  # Your Mailjet sender email
    msg['To'] = recipient_email

    # Create a Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Create the email message
    message = {
        'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()
    }

    # Send the email
    try:
        service.users().messages().send(userId='me', body=message).execute()
        print(f"Email sent to {recipient_email} for team {team_name}.")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

def main():
    # Authenticate and get Gmail credentials
    creds = authenticate_gmail()

    # Path to your CSV file
    csv_file_path = r'C:\Users\Designuser\Desktop\SCOREit\scripts\team_info.csv'

    # Read the CSV file
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)  # Use DictReader for easier access to columns
        for row in csv_reader:
            team_name = row['Team Name']  # Column name for team name
            coach_email = row['Coach email']  # Column name for coach email
            send_email(creds, team_name, coach_email)

if __name__ == "__main__":
    main()
