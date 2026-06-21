"""
STORE assets in a Google Ads account.

Shows how to create the four asset types you asked about:
  - TEXT      (a headline / description string)
  - IMAGE     (uploaded from a local file or a URL)
  - VIDEO     (a YouTube video id)
  - SITELINK  (a link with link text shown under an ad)

Each "create" returns a resource_name like:
    customers/1234567890/assets/55555
That resource_name is the asset's permanent ID — save it; you reuse it when
you later FETCH or USE (link) the asset.

Usage:
    python store_assets.py
Edit CUSTOMER_ID below to your test account (digits only, no dashes).
"""

import uuid

import requests
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"  # <-- your TEST client account id, digits only


def create_text_asset(client, customer_id, text):
    """A text asset is a reusable headline or description string."""
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.text_asset.text = text
    response = service.mutate_assets(customer_id=customer_id, operations=[op])
    return response.results[0].resource_name


def create_image_asset(client, customer_id, image_bytes, name):
    """An image asset holds the raw bytes of a picture (logo, banner, etc.)."""
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = name  # a friendly name; must be unique per account
    asset.type_ = client.enums.AssetTypeEnum.IMAGE
    asset.image_asset.data = image_bytes
    response = service.mutate_assets(customer_id=customer_id, operations=[op])
    return response.results[0].resource_name


def create_youtube_video_asset(client, customer_id, youtube_video_id, name):
    """A video asset references a YouTube video by its id (the v= part of the URL)."""
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = name
    asset.youtube_video_asset.youtube_video_id = youtube_video_id
    response = service.mutate_assets(customer_id=customer_id, operations=[op])
    return response.results[0].resource_name


def create_sitelink_asset(client, customer_id, link_text, description1,
                          description2, final_url):
    """A sitelink asset is an extra link (with text) shown beneath an ad."""
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    sitelink = asset.sitelink_asset
    sitelink.link_text = link_text
    sitelink.description1 = description1
    sitelink.description2 = description2
    asset.final_urls.append(final_url)
    response = service.mutate_assets(customer_id=customer_id, operations=[op])
    return response.results[0].resource_name


def load_image_bytes_from_url(url):
    """Helper: download an image so we can upload its bytes."""
    return requests.get(url, timeout=30).content


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")

    try:
        # 1) TEXT
        text_rn = create_text_asset(
            client, CUSTOMER_ID, "Best Coffee In Town"
        )
        print("Text asset:    ", text_rn)

        # 2) IMAGE (downloads a sample image, then uploads its bytes)
        image_bytes = load_image_bytes_from_url(
            "https://gaagl.page.link/Eit5"  # Google's sample test image
        )
        image_rn = create_image_asset(
            client, CUSTOMER_ID, image_bytes,
            name=f"My Test Image Asset {uuid.uuid4().hex[:6]}"
        )
        print("Image asset:   ", image_rn)

        # 3) VIDEO (any public YouTube video id works for testing)
        video_rn = create_youtube_video_asset(
            client, CUSTOMER_ID, youtube_video_id="dQw4w9WgXcQ",
            name=f"My Test Video Asset {uuid.uuid4().hex[:6]}"
        )
        print("Video asset:   ", video_rn)

        # 4) SITELINK
        sitelink_rn = create_sitelink_asset(
            client, CUSTOMER_ID,
            link_text="Our Menu",
            description1="Fresh roasted daily",
            description2="Dine in or takeaway",
            final_url="https://example.com/menu",
        )
        print("Sitelink asset:", sitelink_rn)

    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")


if __name__ == "__main__":
    main()
