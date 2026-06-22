"""
Generate a refresh token for the YouTube Data API (video upload scope).

This is SEPARATE from the Google Ads token: uploading to YouTube needs the
youtube.upload scope, which the Ads token does not have. It reuses your
existing OAuth Client ID/Secret from google-ads.yaml.

Prerequisites (do these once in Google Cloud Console, same project as your
OAuth client):
  1. Enable "YouTube Data API v3".
  2. On the OAuth consent screen, add the scope
     https://www.googleapis.com/auth/youtube.upload
     and make sure your Google account is a Test user.

Usage:
    python generate_youtube_token.py
Writes youtube_token.json (git-ignored). Sign in with the Google account that
owns the channel you want to upload to.
"""

import json

import yaml
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    cfg = yaml.safe_load(open("google-ads.yaml"))
    client_config = {
        "installed": {
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    data = {
        "refresh_token": creds.refresh_token,
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    with open("youtube_token.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved youtube_token.json — you can now run upload_youtube_video.py")


if __name__ == "__main__":
    main()
