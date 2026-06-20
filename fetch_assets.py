"""
FETCH (list) assets already stored in a Google Ads account.

Uses GAQL (Google Ads Query Language) — it looks like SQL. You SELECT fields
FROM the `asset` resource and optionally filter with WHERE.

Usage:
    python fetch_assets.py
Edit CUSTOMER_ID below to your account (digits only, no dashes).
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"  # <-- your TEST client account id, digits only


def fetch_all_assets(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")

    # Select common fields. asset.type tells you which kind it is.
    query = """
        SELECT
            asset.id,
            asset.name,
            asset.type,
            asset.text_asset.text,
            asset.youtube_video_asset.youtube_video_id,
            asset.sitelink_asset.link_text,
            asset.resource_name
        FROM asset
        ORDER BY asset.id
    """

    # search_stream is efficient for potentially large result sets.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    print(f"{'TYPE':<12} {'ID':<12} NAME / CONTENT")
    print("-" * 60)
    for batch in stream:
        for row in batch.results:
            asset = row.asset
            asset_type = asset.type_.name

            # Pick the most useful descriptor depending on the type.
            if asset_type == "TEXT":
                detail = asset.text_asset.text
            elif asset_type == "YOUTUBE_VIDEO":
                detail = asset.youtube_video_asset.youtube_video_id
            elif asset_type == "SITELINK":
                detail = asset.sitelink_asset.link_text
            else:
                detail = asset.name

            print(f"{asset_type:<12} {asset.id:<12} {detail}")


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    try:
        fetch_all_assets(client, CUSTOMER_ID)
    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")


if __name__ == "__main__":
    main()
