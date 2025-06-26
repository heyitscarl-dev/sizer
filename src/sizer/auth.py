import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from rich.console import Console

TOKEN = "token.json";
CREDS = "creds.json";

SCOPES = ["https://www.googleapis.com/auth/drive"];

console = Console()

def auth():
    # initialize credentials to `None`
    # -> fail by default
    credentials = None

    # check if there's an active token
    if os.path.exists(TOKEN):
        credentials = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    # check if prev. step failed
    if not credentials or not credentials.valid:
        # check if refresh-able...
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        # ...otherwise request new token from credentials...
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS,
                scopes=SCOPES
            )
            credentials = flow.run_local_server(port = 0)
        # ...and write the new token to disk
        with open(TOKEN, "w") as token:
            token.write(credentials.to_json())

    return credentials
