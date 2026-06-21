"""
USE an asset = link it to a campaign.

This script is self-contained and safe to re-run: each run creates a fresh
sitelink asset and a fresh paused Search campaign, then links them together.
That avoids "duplicate name" / "link already exists" errors during a demo.

Usage:
    python use_assets.py
"""

import uuid

import ads_toolkit as t

CUSTOMER_ID = "8076057701"  # your TEST client account id, digits only


def main():
    client = t.get_client()

    # 1) Create a sitelink asset (the thing we will "use")
    sitelink_rn = t.add_sitelink_asset(
        client, CUSTOMER_ID,
        link_text="Our Menu",
        description1="Fresh roasted daily",
        description2="Dine in or takeaway",
        final_url="https://example.com",
    )
    print("Sitelink asset created:", sitelink_rn)

    # 2) Create a paused Search campaign to attach it to
    campaign_rn, campaign_id = t.create_search_campaign(
        client, CUSTOMER_ID, name=f"Search Campaign {uuid.uuid4().hex[:6]}")
    print("Search campaign created:", campaign_rn)

    # 3) USE the asset: link the sitelink to the campaign
    link_rn = t.link_asset_to_campaign(
        client, CUSTOMER_ID, campaign_id, sitelink_rn, "SITELINK")
    print("Linked sitelink to campaign:", link_rn)


if __name__ == "__main__":
    main()
