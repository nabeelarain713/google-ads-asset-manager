"""
Download assets locally.

  * IMAGE assets -> saved as files in the ./downloads folder.
  * VIDEO assets -> the API only exposes a YouTube link (not the raw file),
    so their links are written to ./downloads/video_links.txt.

Usage:
    python download_assets.py
"""

import ads_toolkit as t

CUSTOMER_ID = "8076057701"


def main():
    client = t.get_client()

    images = t.download_image_assets(client, CUSTOMER_ID, out_dir="downloads")
    print(f"Downloaded {len(images)} image file(s):")
    for p in images:
        print("  ", p)

    path, count = t.export_video_links(client, CUSTOMER_ID, out_dir="downloads")
    print(f"\nExported {count} video link(s) to: {path}")
    print("(Google Ads stores videos as YouTube references, so only links are "
          "available via the API — not the raw video files.)")


if __name__ == "__main__":
    main()
