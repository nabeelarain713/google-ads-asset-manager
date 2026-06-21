# 🎥 Demo / Recording Guide

A clean, top-to-bottom run for recording. Starts from creating the Python
environment and ends with everything visible in the test account.

> Credentials (the browser-side setup) are assumed done and stored in
> `google-ads.yaml`. **Do not show `google-ads.yaml` on camera — it has secrets.**

---

## 0. Prerequisites (one-time, browser side)

Already set up. Mention these on camera as "what you need first":

1. Google Ads account + **Manager (MCC)** account
2. **Developer token** (Manager → API Center)
3. **Test manager + test client account** (separate Google account)
4. **Google Cloud project** with "Google Ads API" enabled + **OAuth Client** (Client ID + Secret)
5. **Refresh token** (from `generate_refresh_token.py`)
6. All of the above saved in **`google-ads.yaml`**

---

## 1. Create the Python environment

```powershell
# Go to the project folder
cd "d:\Google Ads"

# Create a fresh virtual environment
python -m venv venv

# Upgrade pip and install the dependencies
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

This installs the official `google-ads` library and its dependencies
(takes ~1 minute the first time).

---

## 2. Configure credentials (already done — for reference)

```powershell
# Make your private config from the template, then fill it in
copy google-ads.example.yaml google-ads.yaml
```

Edit `google-ads.yaml` and set: `developer_token`, `client_id`,
`client_secret`, `refresh_token`, and `login_customer_id`
(your test **manager** id). The scripts use the test **client** id
`8076057701` as `CUSTOMER_ID`.

---

## 3. Run the demo (in this order)

```powershell
# 1) Prove the credentials work — lists your accessible test accounts
.\venv\Scripts\python.exe list_accessible_accounts.py

# 2) STORE assets (text, image, video, sitelink)
.\venv\Scripts\python.exe store_assets.py

# 3) FETCH / list all assets in the account
.\venv\Scripts\python.exe fetch_assets.py

# 4) USE an asset — creates a Search campaign and links a sitelink to it
.\venv\Scripts\python.exe use_assets.py

# 5) CREATE VIDEO CAMPAIGNS — Demand Gen campaigns using your YouTube video
.\venv\Scripts\python.exe make_video_campaigns.py

# 6) DOWNLOAD assets locally (images -> .\downloads, video links -> a file)
.\venv\Scripts\python.exe download_assets.py
```

What each step shows:

| Step | Output to narrate |
|------|-------------------|
| 1 | `customers/7931609515` (test manager) + `customers/8076057701` (test client) = valid creds |
| 2 | 4 asset resource names created |
| 3 | a table of every asset in the account |
| 4 | sitelink asset + Search campaign + the link between them |
| 5 | 2 Demand Gen video campaigns, each with a video ad using your video |
| 6 | `downloads\<id>.png/.jpg` + `downloads\video_links.txt` |

---

## 4. Show it in the test account (the "it worked" shot)

1. Go to **https://ads.google.com**, signed in as **revonix.tpapps@gmail.com**.
2. Open the **test manager "Revonix" (793-160-9515)** → **test client account (8076057701)**.
   - Test accounts show as **cancelled/closed** — normal; the data is still there.
3. **Campaigns** → see the Search + Demand Gen video campaigns (all **Paused**).
4. **Tools → Shared library → Asset library** → see images, sitelink, video.
5. **Demand Gen campaign → Ads** → the video ad using your YouTube video.

---

## Tips

- Do a **full dry run once** before recording, then clear the terminal and record.
- Optional cleaner prompt: run `.\venv\Scripts\Activate.ps1` once, then use
  `python <script>.py`. If activation is blocked, keep using the explicit path.
- Every campaign is created **PAUSED** — nothing serves or spends.
