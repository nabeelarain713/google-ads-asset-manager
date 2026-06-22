# 🎬 YouTube → Google Ads Video Workflow

Complete guide: take a **local video file**, get it onto **YouTube**, and use it
to build **Demand Gen video campaigns** in Google Ads. Every command is for
**Windows Command Prompt (cmd.exe)**.

```
Local .mp4 ──upload──> YouTube ──make public──> video ID ──> Google Ads video campaign
                                                   │
                                                   └──download──> local .mp4
```

---

## Why this workflow exists

* Google Ads video assets are **YouTube references** — a video must be on
  YouTube before you can use it in an ad. You can't upload a raw `.mp4` to
  Google Ads directly.
* The Google Ads API only ever gives you the **YouTube link** for a video,
  never the file.

So the bridge is YouTube: put your video there, then use its ID in Ads.

---

## 0. One-time setup

You only do this once.

### 0a. Create a YouTube channel
Sign in to https://youtube.com with your channel's Google account →
profile icon → **Settings → Add or manage your channel(s) → Create a channel**
(use a **Brand Account** for a company channel).

### 0b. Enable the YouTube Data API (same Cloud project as Google Ads)
In https://console.cloud.google.com (correct project selected):
1. **APIs & Services → Library** → search **"YouTube Data API v3"** → **Enable**.
2. **OAuth consent screen → Data access** → **Add scope**:
   `https://www.googleapis.com/auth/youtube.upload` → Save.
3. Make sure your channel's Google account is a **Test user**.

### 0c. Install the optional dependencies
```cmd
cd /d "d:\Google Ads"
venv\Scripts\activate.bat
python -m pip install -r requirements-optional.txt
```

### 0d. Generate the YouTube token
```cmd
python generate_youtube_token.py
```
A browser opens → sign in with the **channel owner** account → approve the
"Manage your YouTube videos" permission. This creates `youtube_token.json`
(git-ignored secret).

---

## 1. Upload a local video to YouTube (via API)

```cmd
cd /d "d:\Google Ads"
venv\Scripts\activate.bat

python upload_youtube_video.py "C:\path\to\video.mp4" "Your Video Title"
```

Real example:
```cmd
python upload_youtube_video.py "C:\Users\ARSHMAN LAPTOP\Downloads\selvara_ad.mp4" "Selvara AI Generated Ad"
```

Output:
```
Uploaded! Video id: NSlEXllBNsM
URL: https://www.youtube.com/watch?v=NSlEXllBNsM
```

> Only upload videos you **own or have rights to**. Uploading other people's
> content (e.g. a brand's TV commercial) can get your channel struck/terminated
> by YouTube's Content ID.

> **Timeout (`WinError 10060`)?** It's a transient network hiccup — just run the
> command again.

---

## 2. Make the video PUBLIC (required for Google Ads)

⚠️ Videos uploaded through the API by an **unaudited** Cloud project are forced
to **private**, and private videos **cannot be used in Google Ads**.

So make it public/unlisted one of two ways:

**Option A — YouTube Studio (recommended, instant):**
1. https://studio.youtube.com → **Content**.
2. Click the video → set **Visibility** to **Public** or **Unlisted** → Save.

**Option B — Upload directly through Studio** (skip the API entirely):
Studio → **Create → Upload videos** → drag the file → set **Public/Unlisted** →
Publish. (No audit limitation this way.)

> To make API uploads public automatically, complete YouTube's API audit:
> https://support.google.com/youtube/contact/yt_api_form

---

## 3. Get the video ID

The ID is the part after `v=` in the URL:
```
https://www.youtube.com/watch?v=wNFpIiWqTX0
                                 └────┬────┘
                              the video ID
```

---

## 4. Use the video in a Demand Gen video campaign

Edit `make_video_campaigns.py` and set `youtube_video_id` to your **public**
video's ID:

```python
CAMPAIGNS = [
    {
        "campaign_name": "DG Video - Brand Awareness",
        "youtube_video_id": "wNFpIiWqTX0",     # <-- your PUBLIC video id
        "business_name": "Revonix",
        "headlines": ["Automate Everything", "Work Smarter"],
        "descriptions": ["AI that saves you time.", "Built for your business."],
        "final_url": "https://www.revonix.co/",
    },
]
```

Then run it:
```cmd
python make_video_campaigns.py
```

Output (one block per campaign):
```
[DG Video - Brand Awareness 5dbd37]
  Campaign: customers/8076057701/campaigns/23968799257
  Ad:       customers/8076057701/adGroupAds/197079772225~813813134846
  Video:    customers/8076057701/assets/376715191058
```

Each campaign is created **PAUSED** (it never serves or spends).

---

## 5. (Optional) Download a video back from YouTube

```cmd
python download_youtube_videos.py "https://www.youtube.com/watch?v=wNFpIiWqTX0"
```
Files land in `downloads\videos\`.

* Only download videos you **own or have rights to**.
* Install **ffmpeg** (and add it to PATH) for full-resolution merged downloads;
  without it you get a lower-res single file. Open a **new** terminal after
  changing PATH so ffmpeg is detected.

---

## End-to-end command sequence (copy/paste)

```cmd
cd /d "d:\Google Ads"
venv\Scripts\activate.bat

:: 1) upload your own local video
python upload_youtube_video.py "C:\path\to\your_video.mp4" "My Title"

:: 2) -> make it PUBLIC in YouTube Studio, then copy its video id

:: 3) put the id into make_video_campaigns.py, then:
python make_video_campaigns.py

:: 4) optional: download it back
python download_youtube_videos.py "https://www.youtube.com/watch?v=YOUR_ID"
```

---

## Verify in the test account

Sign in to https://ads.google.com as **revonix.tpapps@gmail.com** →
test client **8076057701** → **Campaigns** → open a Demand Gen campaign →
**Ads** → your video ad plays the uploaded video.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `WinError 10060` timeout on upload | transient network | run the command again |
| Uploaded video is **private** | Cloud project not audited | make it public in Studio, or get audited |
| Video can't be used in Ads | video is private | set it Public/Unlisted first |
| Download fails: "ffmpeg is not installed" | merge needs ffmpeg | install ffmpeg + PATH, or it auto-falls back to a single file |
| Ad disapproved: `DESTINATION_NOT_WORKING` | final URL not live | use a working URL (builder also ignores this for test URLs) |
| `DUPLICATE_CAMPAIGN_NAME` | name already used | the script auto-adds a unique suffix |
