"""
USE a video the API-supported way: a DEMAND GEN campaign with a video ad.

Classic Video campaigns are read-only in the API. Demand Gen is the modern,
fully-creatable campaign type that serves video on YouTube/Discover/Gmail.

Layers we build:
    Logo image asset (square)        <- required by the video ad
    Budget (non-shared)
    Demand Gen Campaign (paused)
    Ad Group (no type)
    Demand Gen Video Responsive Ad   <- references your YouTube video asset

Everything is PAUSED; the test account can't spend anyway.

Usage:
    python create_demandgen_campaign.py
"""

import struct
import uuid
import zlib

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"
# YouTube video asset created earlier by store_assets.py
VIDEO_ASSET = "customers/8076057701/assets/375600965428"


def make_square_png(size=512, color=(66, 133, 244)):
    """Build a solid-color square PNG in memory (valid logo, no PIL needed)."""
    r, g, b = color
    row = b"\x00" + bytes([r, g, b]) * size  # filter byte 0 + RGB pixels
    raw = row * size
    compressed = zlib.compress(raw)

    def chunk(typ, data):
        body = typ + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def create_logo_asset(client, customer_id):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = f"Square Logo {uuid.uuid4()}"
    asset.type_ = client.enums.AssetTypeEnum.IMAGE
    asset.image_asset.data = make_square_png()
    return service.mutate_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    try:
        # 0) Square logo image asset (required by the video ad)
        logo_rn = create_logo_asset(client, CUSTOMER_ID)
        print("Logo asset:", logo_rn)

        # 1) Budget (non-shared)
        bs = client.get_service("CampaignBudgetService")
        bop = client.get_type("CampaignBudgetOperation")
        b = bop.create
        b.name = f"DemandGen Budget {uuid.uuid4()}"
        b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        b.amount_micros = 10_000_000  # 10 PKR/day
        b.explicitly_shared = False
        budget_rn = bs.mutate_campaign_budgets(
            customer_id=CUSTOMER_ID, operations=[bop]
        ).results[0].resource_name
        print("Budget:    ", budget_rn)

        # 2) Demand Gen campaign (Maximize Clicks avoids needing conversions)
        cs = client.get_service("CampaignService")
        cop = client.get_type("CampaignOperation")
        c = cop.create
        c.name = f"DemandGen Campaign {uuid.uuid4()}"
        c.advertising_channel_type = (
            client.enums.AdvertisingChannelTypeEnum.DEMAND_GEN
        )
        c.status = client.enums.CampaignStatusEnum.PAUSED
        c.target_spend = client.get_type("TargetSpend")  # Maximize clicks
        c.campaign_budget = budget_rn
        c.contains_eu_political_advertising = (
            client.enums.EuPoliticalAdvertisingStatusEnum
            .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )
        campaign_rn = cs.mutate_campaigns(
            customer_id=CUSTOMER_ID, operations=[cop]
        ).results[0].resource_name
        print("Campaign:  ", campaign_rn)

        # 3) Ad group (Demand Gen ad groups are created with no type)
        ags = client.get_service("AdGroupService")
        agop = client.get_type("AdGroupOperation")
        ag = agop.create
        ag.name = f"DemandGen Ad Group {uuid.uuid4()}"
        ag.campaign = campaign_rn
        ag.status = client.enums.AdGroupStatusEnum.ENABLED
        adgroup_rn = ags.mutate_ad_groups(
            customer_id=CUSTOMER_ID, operations=[agop]
        ).results[0].resource_name
        print("Ad group:  ", adgroup_rn)

        # 4) Demand Gen Video Responsive Ad
        agas = client.get_service("AdGroupAdService")
        agaop = client.get_type("AdGroupAdOperation")
        aga = agaop.create
        aga.ad_group = adgroup_rn
        aga.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad = aga.ad
        ad.name = f"DemandGen Video Ad {uuid.uuid4()}"
        ad.final_urls.append("https://example.com")

        dg = ad.demand_gen_video_responsive_ad
        # business name (inline text)
        dg.business_name.text = "Revonix"
        # the video itself (references your stored YouTube video asset)
        video = client.get_type("AdVideoAsset")
        video.asset = VIDEO_ASSET
        dg.videos.append(video)
        # logo (references the square image asset we made)
        logo = client.get_type("AdImageAsset")
        logo.asset = logo_rn
        dg.logo_images.append(logo)
        # text assets (inline)
        for t in ["Smart Automation", "AI Solutions"]:
            h = client.get_type("AdTextAsset")
            h.text = t
            dg.headlines.append(h)
        lh = client.get_type("AdTextAsset")
        lh.text = "Intelligent automation for your business"
        dg.long_headlines.append(lh)
        for t in ["Save time with AI automation.", "Custom apps and web solutions."]:
            d = client.get_type("AdTextAsset")
            d.text = t
            dg.descriptions.append(d)

        aga_rn = agas.mutate_ad_group_ads(
            customer_id=CUSTOMER_ID, operations=[agaop]
        ).results[0].resource_name
        print("Video ad:  ", aga_rn)
        print("\nDone — your YouTube video is now used in a Demand Gen ad.")

    except GoogleAdsException as ex:
        print(f"Request failed: {ex.error.code().name}")
        for e in ex.failure.errors:
            path = ".".join(
                fpe.field_name for fpe in e.location.field_path_elements
            )
            print(f"  Error: {e.message} | field: {path}")


if __name__ == "__main__":
    main()
