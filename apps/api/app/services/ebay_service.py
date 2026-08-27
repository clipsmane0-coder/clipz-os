"""
eBay Sell API client.
Handles OAuth 2.0 (authorization code grant) and Inventory / Offer API calls.

Docs:
- OAuth: https://developer.ebay.com/api-docs/static/oauth-authorization-code-grant.html
- Inventory API: https://developer.ebay.com/api-docs/sell/inventory/resources/methods
- Offer API: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods
- Fulfillment API: https://developer.ebay.com/api-docs/sell/fulfillment/resources/methods
"""
import base64
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

logger = logging.getLogger("clipz.ebay")


class EbayApiError(Exception):
    def __init__(self, message: str, status_code: int = 0, response: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class EbayClient:
    """eBay Sell API client — initialized per user with their tokens."""

    # Endpoints
    SANDBOX_OAUTH_URL = "https://auth.sandbox.ebay.com/oauth2/authorize"
    SANDBOX_TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    SANDBOX_API_BASE = "https://api.sandbox.ebay.com"

    PROD_OAUTH_URL = "https://auth.ebay.com/oauth2/authorize"
    PROD_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    PROD_API_BASE = "https://api.ebay.com"

    # Required scopes for draft listing creation
    DEFAULT_SCOPES = [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    ]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        access_token_expires_at: Optional[datetime] = None,
        refresh_token_expires_at: Optional[datetime] = None,
        env: str = "production",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.access_token_expires_at = access_token_expires_at
        self.refresh_token_expires_at = refresh_token_expires_at
        self.env = env

        if env == "sandbox":
            self.oauth_url = self.SANDBOX_OAUTH_URL
            self.token_url = self.SANDBOX_TOKEN_URL
            self.api_base = self.SANDBOX_API_BASE
        else:
            self.oauth_url = self.PROD_OAUTH_URL
            self.token_url = self.PROD_TOKEN_URL
            self.api_base = self.PROD_API_BASE

    # --------------------------------------------------------
    # OAuth 2.0 — Authorization Code Grant
    # --------------------------------------------------------

    def get_authorization_url(self, state: str = "") -> str:
        """Build the eBay OAuth consent URL. User is redirected here to grant access."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.DEFAULT_SCOPES),
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        return f"{self.oauth_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange authorization code for access + refresh tokens."""
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.token_url, headers=headers, data=data)

        if r.status_code != 200:
            raise EbayApiError(
                f"Token exchange failed: {r.status_code}",
                status_code=r.status_code,
                response=r.text,
            )

        body = r.json()
        now = datetime.now(timezone.utc)
        self.access_token = body["access_token"]
        self.refresh_token = body.get("refresh_token", "")
        self.access_token_expires_at = now + timedelta(seconds=body.get("expires_in", 7200))
        self.refresh_token_expires_at = now + timedelta(
            seconds=body.get("refresh_token_expires_in", 47304000)
        )

        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_token_expires_at": self.access_token_expires_at,
            "refresh_token_expires_at": self.refresh_token_expires_at,
        }

    async def refresh_access_token(self) -> str:
        """Refresh the access token using the refresh token. Returns new access token."""
        if not self.refresh_token:
            raise EbayApiError("No refresh token available")

        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": " ".join(self.DEFAULT_SCOPES),
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.token_url, headers=headers, data=data)

        if r.status_code != 200:
            raise EbayApiError(
                f"Token refresh failed: {r.status_code}",
                status_code=r.status_code,
                response=r.text,
            )

        body = r.json()
        now = datetime.now(timezone.utc)
        self.access_token = body["access_token"]
        self.access_token_expires_at = now + timedelta(seconds=body.get("expires_in", 7200))
        if "refresh_token" in body:
            self.refresh_token = body["refresh_token"]
            self.refresh_token_expires_at = now + timedelta(
                seconds=body.get("refresh_token_expires_in", 47304000)
            )

        return self.access_token

    async def _ensure_valid_token(self):
        """Make sure access token is still valid, refresh if needed."""
        if not self.access_token or not self.access_token_expires_at:
            if self.refresh_token:
                await self.refresh_access_token()
            else:
                raise EbayApiError("No access token and no refresh token")
            return

        now = datetime.now(timezone.utc)
        # Refresh if token expires in less than 2 minutes
        if (self.access_token_expires_at - now).total_seconds() < 120:
            logger.info("eBay access token expiring soon, refreshing...")
            await self.refresh_access_token()

    # --------------------------------------------------------
    # Generic API call helper
    # --------------------------------------------------------

    async def _api_call(
        self,
        method: str,
        path: str,
        json_body: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        await self._ensure_valid_token()

        url = f"{self.api_base}{path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.request(
                method, url, headers=headers, json=json_body, params=params
            )

        logger.info(f"eBay API {method} {path} -> {r.status_code}")

        if r.status_code in (200, 201, 204):
            if r.text:
                return r.json()
            return {}

        raise EbayApiError(
            f"eBay API error: {method} {path} returned {r.status_code}",
            status_code=r.status_code,
            response=r.text,
        )

    # --------------------------------------------------------
    # Inventory API — create/update inventory item
    # --------------------------------------------------------

    async def create_or_replace_inventory_item(
        self,
        sku: str,
        title: str,
        description: str,
        brand: str,
        mpn: str,
        upc: Optional[str],
        quantity: int,
        price: float,
        currency: str = "USD",
        image_urls: Optional[list] = None,
        item_specifics: Optional[dict] = None,
        condition: str = "NEW",
        condition_description: Optional[str] = None,
        ship_from_postal_code: str = "90001",
    ) -> dict:
        """
        Create or replace an inventory item (SKU).
        This is the eBay inventory item — NOT a listing yet.
        Docs: https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/createOrReplaceInventoryItem
        """
        product = {
            "title": title,
            "description": description,
            "brand": brand,
            "mpn": mpn,
            "aspects": item_specifics or {},
            "imageUrls": image_urls or [],
            "condition": condition,
        }
        if condition_description:
            product["conditionDescription"] = condition_description

        # Add product identifiers if we have UPC
        if upc:
            product["upc"] = [upc]
            product["epid"] = ""  # eBay product ID — optional

        body = {
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": quantity,
                }
            },
            "condition": condition,
            "product": product,
        }

        return await self._api_call(
            "PUT",
            f"/sell/inventory/v1/inventory_item/{sku}",
            json_body=body,
        )

    async def get_inventory_item(self, sku: str) -> dict:
        return await self._api_call("GET", f"/sell/inventory/v1/inventory_item/{sku}")

    # --------------------------------------------------------
    # Offer API — create an offer (listing) from inventory item
    # --------------------------------------------------------

    async def create_offer(
        self,
        sku: str,
        category_id: str,
        price: float,
        currency: str = "USD",
        quantity: int = 1,
        listing_description: Optional[str] = None,
        marketplace_id: str = "EBAY_US",
        format: str = "FIXED_PRICE",
        duration: str = "GTC",  # Good 'Til Cancelled
        best_offer_accepted: bool = False,
        free_shipping: bool = True,
        shipping_service: str = "USPSFirstClass",
        shipping_cost: float = 0.0,
        handling_time: int = 1,
        ship_from_postal_code: str = "90001",
        returns_accepted: bool = True,
        return_days: int = 30,
        return_policy: str = "MoneyBackOrExchange",
    ) -> dict:
        """
        Create a fixed-price offer (draft listing) from an inventory item.
        Docs: https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/createOffer
        """
        body = {
            "sku": sku,
            "marketplaceId": marketplace_id,
            "format": format,
            "listingDuration": duration,
            "categoryId": category_id,
            "listingDescription": listing_description or "",
            "pricingSummary": {
                "price": {
                    "value": str(price),
                    "currency": currency,
                }
            },
            "quantity": quantity,
            "listingPolicies": {
                "fulfillmentPolicyId": "",  # Need to set up policy first
                "paymentPolicyId": "",
                "returnPolicyId": "",
            },
            "shippingCarrierCode": "USPS",
            "shippingServiceCode": shipping_service,
        }

        # Best offer
        if best_offer_accepted:
            body["listingPolicies"]["bestOfferTerms"] = {
                "bestOfferEnabled": True,
            }

        return await self._api_call("POST", "/sell/inventory/v1/offer", json_body=body)

    async def publish_offer(self, offer_id: str) -> dict:
        """Publish an offer (make it live on eBay)."""
        return await self._api_call(
            "POST", f"/sell/inventory/v1/offer/{offer_id}/publish"
        )

    async def get_offer(self, offer_id: str) -> dict:
        return await self._api_call("GET", f"/sell/inventory/v1/offer/{offer_id}")

    # --------------------------------------------------------
    # Account API — get seller info
    # --------------------------------------------------------

    async def get_seller_profile(self) -> dict:
        """Get the authenticated user's eBay profile."""
        return await self._api_call("GET", "/sell/account/v1/privilege")

    async def get_user(self) -> dict:
        """Get basic user info from identity API."""
        try:
            return await self._api_call("GET", "/commerce/identity/v1/user/")
        except EbayApiError:
            # Fallback — try to get from account
            return {}

    # --------------------------------------------------------
    # Fulfillment API — check orders
    # --------------------------------------------------------

    async def get_orders(self, limit: int = 20, offset: int = 0) -> dict:
        return await self._api_call(
            "GET",
            "/sell/fulfillment/v1/order",
            params={"limit": limit, "offset": offset},
        )
