"""
Test various eBay API endpoints to find one that works from Fly.io
"""
import httpx
import base64

EBAY_APP_ID = "ELVINACQ-ArbSens-PRD-5f8516031-l7108a53"
EBAY_CERT_ID = "PRD-f851603le984-0a58-4b00-9cef-08fa"
EBAY_DEV_ID = "83d5b459-94bd-4963-a899-e694003ecde4"
EBAY_AUTH_TOKEN = "v^1.1#i^1#p^3#I^3#r^1#f^0#t^Ul4xMF84OjVFNEVEMkM3OTk5NTUxRUI0MkJGN0VERDFEOTBBNzUzXzJfMSNFXjI2MA=="


async def test_all_endpoints() -> dict:
    """Test every eBay API endpoint we can find and report which work."""
    results = {}

    # 1. Finding API (the one we know fails with 418)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://svcs.ebay.com/services/search/FindingService/v1",
                params={
                    "OPERATION-NAME": "findItemsAdvanced",
                    "SERVICE-VERSION": "1.13.0",
                    "SECURITY-APPNAME": EBAY_APP_ID,
                    "GLOBAL-ID": "EBAY_US",
                    "keywords": "vitamin d3",
                    "RESPONSE-DATA-FORMAT": "JSON",
                    "paginationInput.entriesPerPage": "2",
                },
            )
            results["finding_api"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:200],
            }
    except Exception as e:
        results["finding_api"] = {"error": str(e)}

    # 2. Browse API with client credentials
    try:
        # First get OAuth token
        auth = base64.b64encode(f"{EBAY_APP_ID}:{EBAY_CERT_ID}".encode()).decode()
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_r = await client.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth}",
                },
                data="grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope",
            )
            results["browse_oauth_token"] = {
                "status": token_r.status_code,
                "body_preview": token_r.text[:300],
            }

            if token_r.status_code == 200:
                token_data = token_r.json()
                access_token = token_data.get("access_token", "")
                # Now try Browse API search
                browse_r = await client.get(
                    "https://api.ebay.com/buy/browse/v1/item_summary/search",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    params={
                        "q": "kirkland vitamin d3",
                        "limit": "3",
                    },
                )
                results["browse_api_search"] = {
                    "status": browse_r.status_code,
                    "body_len": len(browse_r.text),
                    "body_preview": browse_r.text[:500],
                }
    except Exception as e:
        results["browse_api"] = {"error": str(e)}

    # 3. Shopping API
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://open.api.ebay.com/shopping",
                params={
                    "callname": "FindProducts",
                    "version": "967",
                    "appid": EBAY_APP_ID,
                    "siteid": "0",
                    "responseencoding": "JSON",
                    "QueryKeywords": "kirkland vitamin d3",
                    "MaxEntries": "3",
                },
            )
            results["shopping_api"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:300],
            }
    except Exception as e:
        results["shopping_api"] = {"error": str(e)}

    # 4. Trading API (SOAP/XML) - test multiple calls
    try:
        # Test 1: GeteBayOfficialTime (simplest auth test)
        async with httpx.AsyncClient(timeout=15.0) as client:
            xml_body = f"""<?xml version="1.0" encoding="utf-8"?>
<GeteBayOfficialTimeRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{EBAY_AUTH_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
</GeteBayOfficialTimeRequest>"""
            r = await client.post(
                "https://api.ebay.com/ws/api.dll",
                headers={
                    "X-EBAY-API-CALL-NAME": "GeteBayOfficialTime",
                    "X-EBAY-API-SITEID": "0",
                    "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
                    "X-EBAY-API-APP-ID": EBAY_APP_ID,
                    "X-EBAY-API-DEV-ID": EBAY_DEV_ID,
                    "X-EBAY-API-CERT-ID": EBAY_CERT_ID,
                    "Content-Type": "text/xml",
                },
                content=xml_body,
            )
            results["trading_gettime"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:500],
            }

        # Test 2: GetSearchResults
        async with httpx.AsyncClient(timeout=15.0) as client:
            xml_body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetSearchResultsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{EBAY_AUTH_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
  <Query>kirkland vitamin d3</Query>
  <Pagination>
    <EntriesPerPage>2</EntriesPerPage>
    <PageNumber>1</PageNumber>
  </Pagination>
</GetSearchResultsRequest>"""
            r = await client.post(
                "https://api.ebay.com/ws/api.dll",
                headers={
                    "X-EBAY-API-CALL-NAME": "GetSearchResults",
                    "X-EBAY-API-SITEID": "0",
                    "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
                    "X-EBAY-API-APP-ID": EBAY_APP_ID,
                    "X-EBAY-API-DEV-ID": EBAY_DEV_ID,
                    "X-EBAY-API-CERT-ID": EBAY_CERT_ID,
                    "Content-Type": "text/xml",
                },
                content=xml_body,
            )
            results["trading_search"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:800],
            }
    except Exception as e:
        results["trading_api"] = {"error": str(e)}

    # 5. Feed API (different domain)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://api.ebay.com/buy/feed/v1_beta/item",
                params={
                    "feed_type": "item",
                    "category_id": "184634",
                    "marketplace_id": "EBAY_US",
                },
            )
            results["feed_api"] = {
                "status": r.status_code,
                "body_preview": r.text[:200],
            }
    except Exception as e:
        results["feed_api"] = {"error": str(e)}

    return results
