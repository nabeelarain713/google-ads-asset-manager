"""
Create a PAUSED test campaign (so nothing actually runs / costs anything).

A campaign needs two things first:
  1. A campaign BUDGET (how much it can spend per day)
  2. The CAMPAIGN itself (channel type, status, bidding, budget link)

We create both, then print the campaign's id/resource name so use_assets.py
can link an asset to it.

Usage:
    python create_campaign.py
"""

import uuid
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CUSTOMER_ID = "8076057701"  # your TEST client account id, digits only


def create_budget(client, customer_id):
    service = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    budget = op.create
    budget.name = f"Test Budget {uuid.uuid4()}"  # name must be unique
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    # micros = value * 1,000,000. Must be a whole-unit multiple for PKR.
    budget.amount_micros = 10_000_000  # 10 PKR/day
    response = service.mutate_campaign_budgets(
        customer_id=customer_id, operations=[op]
    )
    return response.results[0].resource_name


def create_campaign(client, customer_id, budget_resource_name):
    service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    campaign = op.create
    campaign.name = f"Test Search Campaign {uuid.uuid4()}"
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )
    # PAUSED = created but never serves ads. Safe for testing.
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    # Simple manual bidding (required). Assigning an empty ManualCpc selects it.
    campaign.manual_cpc = client.get_type("ManualCpc")
    # Newer API versions require declaring EU political advertising status.
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum
        .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    campaign.campaign_budget = budget_resource_name
    # Where ads could show (Search only).
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_content_network = False

    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[op]
    )
    return response.results[0].resource_name


def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    try:
        budget_rn = create_budget(client, CUSTOMER_ID)
        print("Budget created:  ", budget_rn)

        campaign_rn = create_campaign(client, CUSTOMER_ID, budget_rn)
        print("Campaign created:", campaign_rn)

        # The numeric id is the last path segment — handy for use_assets.py
        campaign_id = campaign_rn.split("/")[-1]
        print("\nCampaign ID:", campaign_id)
        print("Use this id as CAMPAIGN_ID in use_assets.py")
    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")


if __name__ == "__main__":
    main()
