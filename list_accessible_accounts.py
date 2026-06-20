"""
First test of your credentials.

Lists every Google Ads account your authenticated user can reach. If this
prints account IDs, your developer token + OAuth + refresh token all work.

Usage:
    python list_accessible_accounts.py
"""

from google.ads.googleads.client import GoogleAdsClient


def main():
    # Loads developer_token, client_id, client_secret, refresh_token, etc.
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")

    customer_service = client.get_service("CustomerService")
    accessible = customer_service.list_accessible_customers()

    print("Accessible accounts (resource names):")
    for resource_name in accessible.resource_names:
        # resource_name looks like: customers/1234567890
        print("  ", resource_name)


if __name__ == "__main__":
    main()
