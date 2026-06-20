"""
Generate an OAuth2 refresh token for the Google Ads API.

Run once after you have created an OAuth Client ID (Desktop app) in the
Google Cloud Console. It opens a browser, asks you to approve access, and
prints a refresh token that you paste into google-ads.yaml.

Usage:
    python generate_refresh_token.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# The scope that grants access to the Google Ads API.
SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    print("Paste your OAuth Client ID and Client Secret")
    print("(from Google Cloud Console -> Credentials -> your Desktop OAuth client).\n")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    # Opens a local web server + browser window for you to approve.
    credentials = flow.run_local_server(port=0, prompt="consent")

    print("\n=== SUCCESS ===")
    print("Refresh token (paste this into google-ads.yaml):\n")
    print(credentials.refresh_token)


if __name__ == "__main__":
    main()
