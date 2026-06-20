"""
ads_toolkit.py — reusable helpers for the Google Ads assets workflow.

Import these functions from small runnable scripts. Everything is built
around your test account but works the same on real accounts.

Sections:
  CLIENT   - load the API client
  STORE    - create assets (text, image-from-bytes, YouTube video, sitelink)
  FETCH    - list assets as plain Python dicts
  DOWNLOAD - save image asset files to disk; export video YouTube links
  USE      - reusable Demand Gen video campaign builder; generic asset linker

Notes / API constraints (important):
  * Video assets are YouTube *references* (a video id). You cannot upload a
    local .mp4 as a video asset; upload it to YouTube first, then use its id.
  * Classic Video campaigns are read-only in the API. Demand Gen is the
    supported way to serve video, so the campaign builder below is Demand Gen.
  * The API exposes image asset files (downloadable URL) but only a YouTube
    link for videos — so download saves images and exports video links.
"""

import os
import struct
import uuid
import zlib

import requests
from google.ads.googleads.client import GoogleAdsClient


# ----------------------------------------------------------------------------
# CLIENT
# ----------------------------------------------------------------------------
def get_client(config_path="google-ads.yaml"):
    """Load a GoogleAdsClient from your yaml config."""
    return GoogleAdsClient.load_from_storage(config_path)


# ----------------------------------------------------------------------------
# STORE
# ----------------------------------------------------------------------------
def add_text_asset(client, customer_id, text):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    op.create.text_asset.text = text
    return service.mutate_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def add_image_asset(client, customer_id, image_bytes, name):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = name
    asset.type_ = client.enums.AssetTypeEnum.IMAGE
    asset.image_asset.data = image_bytes
    return service.mutate_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def add_youtube_video_asset(client, customer_id, youtube_video_id, name):
    """Store a video asset. The video must already exist on YouTube."""
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = name
    asset.youtube_video_asset.youtube_video_id = youtube_video_id
    return service.mutate_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def add_sitelink_asset(client, customer_id, link_text, description1,
                       description2, final_url):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    sl = op.create.sitelink_asset
    sl.link_text = link_text
    sl.description1 = description1
    sl.description2 = description2
    op.create.final_urls.append(final_url)
    return service.mutate_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def make_square_png(size=512, color=(66, 133, 244)):
    """Generate a solid-color square PNG in memory (a valid logo, no PIL)."""
    r, g, b = color
    raw = (b"\x00" + bytes([r, g, b]) * size) * size

    def chunk(typ, data):
        body = typ + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) \
        + chunk(b"IEND", b"")


# ----------------------------------------------------------------------------
# FETCH
# ----------------------------------------------------------------------------
def list_assets(client, customer_id, asset_type=None):
    """
    Return assets as a list of dicts. Optionally filter by type string,
    e.g. 'IMAGE', 'YOUTUBE_VIDEO', 'TEXT', 'SITELINK'.
    """
    ga = client.get_service("GoogleAdsService")
    where = f"WHERE asset.type = '{asset_type}'" if asset_type else ""
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.type,
            asset.resource_name,
            asset.text_asset.text,
            asset.image_asset.full_size.url,
            asset.image_asset.mime_type,
            asset.youtube_video_asset.youtube_video_id,
            asset.sitelink_asset.link_text
        FROM asset
        {where}
        ORDER BY asset.id
    """
    out = []
    for batch in ga.search_stream(customer_id=customer_id, query=query):
        for row in batch.results:
            a = row.asset
            out.append({
                "id": a.id,
                "name": a.name,
                "type": a.type_.name,
                "resource_name": a.resource_name,
                "text": a.text_asset.text,
                "image_url": a.image_asset.full_size.url,
                "image_mime": a.image_asset.mime_type.name,
                "youtube_id": a.youtube_video_asset.youtube_video_id,
                "sitelink_text": a.sitelink_asset.link_text,
            })
    return out


# ----------------------------------------------------------------------------
# DOWNLOAD
# ----------------------------------------------------------------------------
_MIME_EXT = {
    "IMAGE_JPEG": "jpg", "IMAGE_PNG": "png", "IMAGE_GIF": "gif",
}


def download_image_assets(client, customer_id, out_dir="downloads"):
    """Download every image asset's file to out_dir. Returns saved paths."""
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for a in list_assets(client, customer_id, asset_type="IMAGE"):
        url = a["image_url"]
        if not url:
            continue  # not all image assets expose a downloadable url
        ext = _MIME_EXT.get(a["image_mime"], "bin")
        path = os.path.join(out_dir, f"{a['id']}.{ext}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        saved.append(path)
    return saved


def export_video_links(client, customer_id, out_dir="downloads"):
    """Write YouTube links for all video assets to a text file. Returns path."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "video_links.txt")
    videos = list_assets(client, customer_id, asset_type="YOUTUBE_VIDEO")
    with open(path, "w", encoding="utf-8") as f:
        for a in videos:
            vid = a["youtube_id"]
            f.write(f"{a['id']}\t{a['name']}\thttps://www.youtube.com/watch?v={vid}\n")
    return path, len(videos)


# ----------------------------------------------------------------------------
# USE
# ----------------------------------------------------------------------------
def link_asset_to_campaign(client, customer_id, campaign_id, asset_rn,
                           field_type_name):
    """Generic: link any asset to a campaign with a given field type name."""
    service = client.get_service("CampaignAssetService")
    op = client.get_type("CampaignAssetOperation")
    ca = op.create
    ca.asset = asset_rn
    ca.campaign = client.get_service("CampaignService").campaign_path(
        customer_id, campaign_id)
    ca.field_type = getattr(client.enums.AssetFieldTypeEnum, field_type_name)
    return service.mutate_campaign_assets(
        customer_id=customer_id, operations=[op]
    ).results[0].resource_name


def create_demandgen_video_campaign(
    client, customer_id, *,
    campaign_name,
    youtube_video_id=None,   # provide an id to create the video asset, OR
    video_asset=None,        # provide an existing video asset resource name
    business_name="My Business",
    headlines=None,
    long_headlines=None,
    descriptions=None,
    logo_asset=None,         # existing image asset; if None, a logo is generated
    final_url="https://example.com",
    daily_budget_micros=10_000_000,
):
    """
    Reusable builder: makes a paused Demand Gen campaign that uses a video.
    Returns a dict of the resource names it created.

    Call it repeatedly with different inputs to build different campaigns.
    """
    headlines = headlines or ["Smart Automation", "AI Solutions"]
    long_headlines = long_headlines or ["Intelligent automation for your business"]
    descriptions = descriptions or ["Save time with AI automation.",
                                    "Custom apps and web solutions."]

    # video asset: create from id if a resource name wasn't supplied
    if not video_asset:
        if not youtube_video_id:
            raise ValueError("Provide youtube_video_id or video_asset")
        video_asset = add_youtube_video_asset(
            client, customer_id, youtube_video_id, f"Video {uuid.uuid4()}")

    # logo: generate a square one if not supplied
    if not logo_asset:
        logo_asset = add_image_asset(
            client, customer_id, make_square_png(), f"Logo {uuid.uuid4()}")

    # budget (non-shared)
    bs = client.get_service("CampaignBudgetService")
    bop = client.get_type("CampaignBudgetOperation")
    b = bop.create
    b.name = f"Budget {uuid.uuid4()}"
    b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    b.amount_micros = daily_budget_micros
    b.explicitly_shared = False
    budget_rn = bs.mutate_campaign_budgets(
        customer_id=customer_id, operations=[bop]).results[0].resource_name

    # campaign
    cs = client.get_service("CampaignService")
    cop = client.get_type("CampaignOperation")
    c = cop.create
    c.name = campaign_name
    c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.DEMAND_GEN
    c.status = client.enums.CampaignStatusEnum.PAUSED
    c.target_spend = client.get_type("TargetSpend")  # Maximize clicks
    c.campaign_budget = budget_rn
    c.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum
        .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
    campaign_rn = cs.mutate_campaigns(
        customer_id=customer_id, operations=[cop]).results[0].resource_name

    # ad group (Demand Gen: created with no type)
    ags = client.get_service("AdGroupService")
    agop = client.get_type("AdGroupOperation")
    ag = agop.create
    ag.name = f"Ad Group {uuid.uuid4()}"
    ag.campaign = campaign_rn
    ag.status = client.enums.AdGroupStatusEnum.ENABLED
    adgroup_rn = ags.mutate_ad_groups(
        customer_id=customer_id, operations=[agop]).results[0].resource_name

    # demand gen video responsive ad
    agas = client.get_service("AdGroupAdService")
    agaop = client.get_type("AdGroupAdOperation")
    aga = agaop.create
    aga.ad_group = adgroup_rn
    aga.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad = aga.ad
    ad.name = f"Video Ad {uuid.uuid4()}"
    ad.final_urls.append(final_url)
    dg = ad.demand_gen_video_responsive_ad
    dg.business_name.text = business_name
    v = client.get_type("AdVideoAsset")
    v.asset = video_asset
    dg.videos.append(v)
    lg = client.get_type("AdImageAsset")
    lg.asset = logo_asset
    dg.logo_images.append(lg)
    for t in headlines:
        x = client.get_type("AdTextAsset"); x.text = t; dg.headlines.append(x)
    for t in long_headlines:
        x = client.get_type("AdTextAsset"); x.text = t; dg.long_headlines.append(x)
    for t in descriptions:
        x = client.get_type("AdTextAsset"); x.text = t; dg.descriptions.append(x)
    # Allow ads whose destination URL isn't live yet (test/staging links).
    agaop.policy_validation_parameter.ignorable_policy_topics.append(
        "DESTINATION_NOT_WORKING")
    ad_rn = agas.mutate_ad_group_ads(
        customer_id=customer_id, operations=[agaop]).results[0].resource_name

    return {
        "video_asset": video_asset,
        "logo_asset": logo_asset,
        "budget": budget_rn,
        "campaign": campaign_rn,
        "ad_group": adgroup_rn,
        "ad": ad_rn,
        "campaign_id": campaign_rn.split("/")[-1],
    }
