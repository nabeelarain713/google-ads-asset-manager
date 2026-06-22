"""
Download YouTube videos to disk with yt-dlp.

------------------------------------------------------------------------------
USE ONLY for videos you OWN or have explicit permission/rights to download.
Downloading other people's YouTube videos violates YouTube's Terms of Service.
For Google Ads video campaigns the video must be on your own channel anyway,
so the videos you actually use in ads are yours to download.
------------------------------------------------------------------------------

This is an OPTIONAL helper, separate from the Google Ads API: the Ads API only
gives you a YouTube *link* for a video asset, never the file. This script takes
those links (or any you pass) and downloads the files via yt-dlp.

Install the optional dependency first:
    pip install yt-dlp
(High-quality merges also need ffmpeg installed and on your PATH.)

Usage:
    python download_youtube_videos.py                  # reads downloads/video_links.txt
    python download_youtube_videos.py <url> [<url> ...] # download specific URLs
"""

import os
import shutil
import sys

OUT_DIR = "downloads/videos"
LINKS_FILE = "downloads/video_links.txt"


def read_links(path):
    """Read URLs from the tab-separated file written by download_assets.py."""
    urls = []
    if not os.path.exists(path):
        return urls
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if parts and parts[-1].startswith("http"):
                urls.append(parts[-1])
    return urls


def download(urls, out_dir=OUT_DIR):
    # Imported here so the rest of the project doesn't require yt-dlp.
    try:
        import yt_dlp
    except ImportError:
        sys.exit("yt-dlp is not installed. Run:  pip install yt-dlp")

    os.makedirs(out_dir, exist_ok=True)
    opts = {"outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s")}

    if shutil.which("ffmpeg"):
        # Prefer H.264 video + AAC (m4a) audio so the merged MP4 plays in every
        # player. (Default "bestaudio" is often Opus, which is valid but many
        # players can't decode Opus inside an MP4 -> video plays with no sound.)
        opts["format"] = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        opts["merge_output_format"] = "mp4"
    else:
        # No ffmpeg: grab the best single pre-merged file (no merge needed).
        print("Note: ffmpeg not found — downloading best single-file format. "
              "Install ffmpeg for higher-resolution merged downloads.")
        opts["format"] = "best"

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download(urls)


def main():
    # URLs from the command line, otherwise from the links file.
    urls = sys.argv[1:] or read_links(LINKS_FILE)
    if not urls:
        sys.exit(f"No URLs given and none found in {LINKS_FILE}. "
                 f"Run download_assets.py first, or pass URLs as arguments.")

    print("=" * 70)
    print("REMINDER: only download videos you OWN or are authorized to download.")
    print("=" * 70)
    print(f"Downloading {len(urls)} video(s) to {OUT_DIR}/ ...")
    download(urls)
    print("Done.")


if __name__ == "__main__":
    main()
