"""
Create DIFFERENT video (Demand Gen) campaigns using the reusable builder.

This shows the point of ads_toolkit.create_demandgen_video_campaign: call it
with different inputs to spin up as many distinct campaigns as you like.

Usage:
    python make_video_campaigns.py
Edit the CAMPAIGNS list below to define your own.
"""

import uuid

import ads_toolkit as t

CUSTOMER_ID = "8076057701"

# Each dict is one campaign. Add/remove entries freely.
CAMPAIGNS = [
    {
        "campaign_name": "DG Video - Brand Awareness",
        "youtube_video_id": "wNFpIiWqTX0",
        "business_name": "Revonix",
        "headlines": ["Automate Everything", "Work Smarter"],
        "descriptions": ["AI that saves you time.", "Built for your business."],
        "final_url": "https://www.revonix.co/",
    },
    {
        "campaign_name": "DG Video - Product Launch",
        "youtube_video_id": "wNFpIiWqTX0",
        "business_name": "Revonix",
        "headlines": ["New: AI Workflows", "Launch Day"],
        "long_headlines": ["Introducing our new AI automation platform"],
        "descriptions": ["See what's new.", "Try it today."],
        "final_url": "https://www.revonix.co/",
    },
]


def main():
    client = t.get_client()
    for spec in CAMPAIGNS:
        spec = dict(spec)  # copy so we can tweak the name
        # Campaign names must be unique per account — add a short suffix.
        spec["campaign_name"] = f"{spec['campaign_name']} {uuid.uuid4().hex[:6]}"
        result = t.create_demandgen_video_campaign(client, CUSTOMER_ID, **spec)
        print(f"\n[{spec['campaign_name']}]")
        print("  Campaign:", result["campaign"])
        print("  Ad:      ", result["ad"])
        print("  Video:   ", result["video_asset"])


if __name__ == "__main__":
    main()
