"""
USE an asset = link a stored asset to something (here, a campaign).

An asset on its own does nothing until you attach it. You attach it with a
"link" resource and a `field_type` that says what role it plays
(SITELINK, YOUTUBE_VIDEO, MARKETING_IMAGE, etc.).

This example links a SITELINK asset to a campaign via CampaignAssetService.

Usage:
    python use_assets.py
Fill in CUSTOMER_ID, CAMPAIGN_ID, and ASSET_RESOURCE_NAME below
(get the asset resource name from store_assets.py or fetch_assets.py).
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"            # your TEST client account id, digits only
CAMPAIGN_ID = "23959904774"           # the paused campaign from create_campaign.py
ASSET_RESOURCE_NAME = "customers/8076057701/assets/375665857041"  # "Our Menu" sitelink


def link_sitelink_to_campaign(client, customer_id, campaign_id, asset_rn):
    service = client.get_service("CampaignAssetService")
    op = client.get_type("CampaignAssetOperation")

    campaign_asset = op.create
    campaign_asset.asset = asset_rn
    campaign_asset.campaign = client.get_service(
        "CampaignService"
    ).campaign_path(customer_id, campaign_id)
    # field_type must match the asset type you are linking.
    campaign_asset.field_type = client.enums.AssetFieldTypeEnum.SITELINK

    response = service.mutate_campaign_assets(
        customer_id=customer_id, operations=[op]
    )
    return response.results[0].resource_name


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    try:
        link_rn = link_sitelink_to_campaign(
            client, CUSTOMER_ID, CAMPAIGN_ID, ASSET_RESOURCE_NAME
        )
        print("Linked! Campaign-asset link:", link_rn)
    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")


if __name__ == "__main__":
    main()
