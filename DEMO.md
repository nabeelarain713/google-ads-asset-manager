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

> Create the venv with **`py -3.12`** explicitly. Plain `python` is ambiguous on
> this machine (there is also a 3.14) and mixing versions breaks grpc.

**Command Prompt (cmd.exe):**

```cmd
cd /d "d:\Google Ads"

:: Create the venv with Python 3.12 explicitly
py -3.12 -m venv venv

:: Activate it (cmd uses activate.bat). Prompt then shows (venv).
venv\Scripts\activate.bat

:: Install the official google-ads library + dependencies (~1 min first time)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**PowerShell:**

```powershell
cd "d:\Google Ads"

# Create the venv with Python 3.12 explicitly
py -3.12 -m venv venv

# Activate it (PowerShell uses Activate.ps1). Prompt then shows (venv).
.\venv\Scripts\Activate.ps1

# Install the official google-ads library + dependencies (~1 min first time)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> If PowerShell blocks activation with an execution-policy error, either run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or skip
> activation and call scripts with the full path `.\venv\Scripts\python.exe <script>.py`.
>
> If you ever see `ImportError: cannot import name 'cygrpc'`, the venv was
> built with a different Python than its packages. Fix: delete and rebuild
> with one version — `rmdir /s /q venv` (cmd) or `Remove-Item -Recurse -Force venv`
> (PowerShell), then `py -3.12 -m venv venv`.

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

With the venv activated (step 1), just use `python` — the commands are the
same in both cmd and PowerShell:

```text
python list_accessible_accounts.py
python store_assets.py
python fetch_assets.py
python use_assets.py
python make_video_campaigns.py
python download_assets.py
```

> Not activated? Use the full path instead:
> cmd → `venv\Scripts\python.exe <script>.py`
> PowerShell → `.\venv\Scripts\python.exe <script>.py`

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
