"""
Upload a local video file to YOUR OWN YouTube channel via the YouTube Data API.

The returned video id can be used as a Google Ads video asset
(see ads_toolkit.add_youtube_video_asset / create_demandgen_video_campaign).

IMPORTANT: If your Google Cloud project has not passed YouTube's API audit,
uploaded videos are forced to PRIVATE no matter what privacy you request, and
cannot be used in Google Ads until the project is verified. For Ads use now,
upload via YouTube Studio (the website) instead.

Setup:
    pip install -r requirements-optional.txt
    python generate_youtube_token.py     # one time, creates youtube_token.json

Usage:
    python upload_youtube_video.py "C:\\path\\to\\video.mp4" "My Title"
    python upload_youtube_video.py "video.mp4" "My Title" --privacy unlisted
"""

import argparse
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service(token_file="youtube_token.json"):
    d = json.load(open(token_file, encoding="utf-8"))
    creds = Credentials(
        token=None,
        refresh_token=d["refresh_token"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
        token_uri=d["token_uri"],
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def upload_video(file_path, title, description="", tags=None, privacy="unlisted"):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
        },
        "status": {
            "privacyStatus": privacy,        # honored only if project is verified
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media)

    print(f"Uploading {file_path} ...")
    response = request.execute()
    video_id = response["id"]
    print("Uploaded! Video id:", video_id)
    print("URL:", f"https://www.youtube.com/watch?v={video_id}")
    print("Use this id as a Google Ads video asset (youtube_video_id).")
    return video_id


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", help="path to the local video file")
    p.add_argument("title", help="video title")
    p.add_argument("--description", default="")
    p.add_argument("--privacy", default="unlisted",
                   choices=["private", "unlisted", "public"])
    args = p.parse_args()
    upload_video(args.file, args.title,
                 description=args.description, privacy=args.privacy)


if __name__ == "__main__":
    main()
