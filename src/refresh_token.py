import os
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Path to your OAuth 2.0 Client Secret JSON file
CLIENT_SECRET_FILE = 'credentials.json'  # Update this with the path to your client secret file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Initialize the OAuth flow
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

# Run the OAuth flow to get the credentials
creds = flow.run_local_server(port=0)

# Print the new tokens
print('Access Token:', creds.token)
print('Refresh Token:', creds.refresh_token)

# Save the credentials to a file
token_data = {
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': creds.scopes,
    'expiry': creds.expiry.isoformat() if creds.expiry else None
}

with open('token.json', 'w') as token_file:
    json.dump(token_data, token_file)

print('New tokens have been saved to token.json')
