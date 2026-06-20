"""
USE a video = put your YouTube video asset into a VIDEO campaign as an ad.

A standard Search campaign can't show video. Videos live in VIDEO campaigns,
where the video itself IS the ad. Building one needs four layers:

    Budget -> Video Campaign -> Ad Group -> Video Ad (references the video asset)

Everything is PAUSED so nothing runs. Test accounts never spend anyway.

Usage:
    python create_video_campaign.py
"""

import uuid
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"
# The YouTube video asset created earlier by store_assets.py
VIDEO_ASSET = "customers/8076057701/assets/375600965428"


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    try:
        # 1) Budget
        bs = client.get_service("CampaignBudgetService")
        bop = client.get_type("CampaignBudgetOperation")
        b = bop.create
        b.name = f"Video Budget {uuid.uuid4()}"
        b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        b.amount_micros = 10_000_000  # 10 PKR/day
        b.explicitly_shared = False  # dedicated to one campaign (video needs this)
        budget_rn = bs.mutate_campaign_budgets(
            customer_id=CUSTOMER_ID, operations=[bop]
        ).results[0].resource_name
        print("Budget:    ", budget_rn)

        # 2) Video campaign (Target CPM bidding suits bumper ads)
        cs = client.get_service("CampaignService")
        cop = client.get_type("CampaignOperation")
        c = cop.create
        c.name = f"Video Campaign {uuid.uuid4()}"
        c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.VIDEO
        c.status = client.enums.CampaignStatusEnum.PAUSED
        c.target_cpm = client.get_type("TargetCpm")
        c.campaign_budget = budget_rn
        c.contains_eu_political_advertising = (
            client.enums.EuPoliticalAdvertisingStatusEnum
            .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )
        campaign_rn = cs.mutate_campaigns(
            customer_id=CUSTOMER_ID, operations=[cop]
        ).results[0].resource_name
        print("Campaign:  ", campaign_rn)

        # 3) Ad group (bumper = short 6-second video format)
        ags = client.get_service("AdGroupService")
        agop = client.get_type("AdGroupOperation")
        ag = agop.create
        ag.name = f"Video Ad Group {uuid.uuid4()}"
        ag.campaign = campaign_rn
        ag.type_ = client.enums.AdGroupTypeEnum.VIDEO_BUMPER
        ag.status = client.enums.AdGroupStatusEnum.ENABLED
        adgroup_rn = ags.mutate_ad_groups(
            customer_id=CUSTOMER_ID, operations=[agop]
        ).results[0].resource_name
        print("Ad group:  ", adgroup_rn)

        # 4) The video ad itself, referencing your YouTube video asset
        agas = client.get_service("AdGroupAdService")
        agaop = client.get_type("AdGroupAdOperation")
        aga = agaop.create
        aga.ad_group = adgroup_rn
        aga.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad = aga.ad
        ad.final_urls.append("https://example.com")
        ad.video_ad.video.asset = VIDEO_ASSET
        # Bumper format (empty info object selects the format)
        ad.video_ad.bumper = client.get_type("VideoBumperInStreamAdInfo")
        aga_rn = agas.mutate_ad_group_ads(
            customer_id=CUSTOMER_ID, operations=[agaop]
        ).results[0].resource_name
        print("Video ad:  ", aga_rn)
        print("\nDone — your video is now used inside a video campaign.")

    except GoogleAdsException as ex:
        print(f"Request failed: {ex.error.code().name}")
        for e in ex.failure.errors:
            path = ".".join(
                fpe.field_name for fpe in e.location.field_path_elements
            )
            print(f"  Error: {e.message} | field: {path}")


if __name__ == "__main__":
    main()
