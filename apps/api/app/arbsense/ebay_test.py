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

    # 2. Browse API with client credentials - multiple approaches
    try:
        # Approach A: Basic auth with URL-encoded credentials
        from urllib.parse import quote_plus
        encoded_id = quote_plus(EBAY_APP_ID)
        encoded_secret = quote_plus(EBAY_CERT_ID)
        auth2 = base64.b64encode(f"{encoded_id}:{encoded_secret}".encode()).decode()
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_r = await client.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth2}",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope/buy.item.browse"
                },
            )
            results["browse_oauth_approach_a"] = {
                "status": token_r.status_code,
                "body_preview": token_r.text[:300],
            }

        # Approach B: Different scope format
        auth3 = base64.b64encode(f"{EBAY_APP_ID}:{EBAY_CERT_ID}".encode()).decode()
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_r = await client.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth3}",
                },
                data="grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope",
            )
            results["browse_oauth_approach_b"] = {
                "status": token_r.status_code,
                "body_preview": token_r.text[:300],
            }

    except Exception as e:
        results["browse_api"] = {"error": str(e)}

    # 2b. Taxonomy API (no auth needed, test if REST endpoints work at all)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://api.ebay.com/commerce/taxonomy/v1/category_tree/default_tree",
                headers={
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                },
            )
            results["taxonomy_api"] = {
                "status": r.status_code,
                "body_preview": r.text[:300],
            }
    except Exception as e:
        results["taxonomy_api"] = {"error": str(e)}

    # 2c. Browse API with no auth (public access?)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                    "X-EBAY-API-IAF-TOKEN": EBAY_APP_ID,
                },
                params={
                    "q": "kirkland vitamin d3",
                    "limit": "2",
                },
            )
            results["browse_no_auth"] = {
                "status": r.status_code,
                "body_preview": r.text[:300],
            }
    except Exception as e:
        results["browse_no_auth"] = {"error": str(e)}

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

    # 4. Trading API (SOAP/XML) - test various calls
    try:
        # Test 1: GetCategories (very basic public call)
        async with httpx.AsyncClient(timeout=15.0) as client:
            xml_body = """<?xml version="1.0" encoding="utf-8"?>
<GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>""" + EBAY_AUTH_TOKEN + """</eBayAuthToken>
  </RequesterCredentials>
  <CategorySiteID>0</CategorySiteID>
  <DetailLevel>ReturnSummary</DetailLevel>
  <LevelLimit>1</LevelLimit>
</GetCategoriesRequest>"""
            r = await client.post(
                "https://api.ebay.com/ws/api.dll",
                headers={
                    "X-EBAY-API-CALL-NAME": "GetCategories",
                    "X-EBAY-API-SITEID": "0",
                    "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
                    "X-EBAY-API-APP-ID": EBAY_APP_ID,
                    "X-EBAY-API-DEV-ID": EBAY_DEV_ID,
                    "X-EBAY-API-CERT-ID": EBAY_CERT_ID,
                    "Content-Type": "text/xml",
                },
                content=xml_body,
            )
            results["trading_getcategories"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:600],
            }

        # Test 2: GetItem with a known item ID
        async with httpx.AsyncClient(timeout=15.0) as client:
            xml_body = """<?xml version="1.0" encoding="utf-8"?>
<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>""" + EBAY_AUTH_TOKEN + """</eBayAuthToken>
  </RequesterCredentials>
  <ItemID>115936073280</ItemID>
</GetItemRequest>"""
            r = await client.post(
                "https://api.ebay.com/ws/api.dll",
                headers={
                    "X-EBAY-API-CALL-NAME": "GetItem",
                    "X-EBAY-API-SITEID": "0",
                    "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
                    "X-EBAY-API-APP-ID": EBAY_APP_ID,
                    "X-EBAY-API-DEV-ID": EBAY_DEV_ID,
                    "X-EBAY-API-CERT-ID": EBAY_CERT_ID,
                    "Content-Type": "text/xml",
                },
                content=xml_body,
            )
            results["trading_getitem"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:800],
            }

        # Test 3: Finding API via POST (instead of GET)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                "https://svcs.ebay.com/services/search/FindingService/v1",
                data={
                    "OPERATION-NAME": "findItemsByKeywords",
                    "SERVICE-VERSION": "1.13.0",
                    "SECURITY-APPNAME": EBAY_APP_ID,
                    "GLOBAL-ID": "EBAY_US",
                    "keywords": "kirkland vitamin d3",
                    "RESPONSE-DATA-FORMAT": "JSON",
                    "paginationInput.entriesPerPage": "2",
                },
                headers={
                    "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
                    "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
                    "X-EBAY-SOA-GLOBAL-ID": "EBAY_US",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            results["finding_api_post"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:300],
            }

        # Test 4: Finding API with SOAP format
        async with httpx.AsyncClient(timeout=15.0) as client:
            soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ser="http://www.ebay.com/marketplace/search/v1/services">
  <soapenv:Header>
    <ser:RequesterCredentials>
      <ser:eBayAuthToken>{EBAY_AUTH_TOKEN}</ser:eBayAuthToken>
    </ser:RequesterCredentials>
  </soapenv:Header>
  <soapenv:Body>
    <ser:findItemsByKeywordsRequest>
      <ser:keywords>kirkland vitamin d3</ser:keywords>
      <ser:paginationInput>
        <ser:entriesPerPage>2</ser:entriesPerPage>
      </ser:paginationInput>
    </ser:findItemsByKeywordsRequest>
  </soapenv:Body>
</soapenv:Envelope>"""
            r = await client.post(
                "https://svcs.ebay.com/services/search/FindingService/v1",
                content=soap_body,
                headers={
                    "Content-Type": "text/xml;charset=UTF-8",
                    "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
                    "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
                },
            )
            results["finding_api_soap"] = {
                "status": r.status_code,
                "body_len": len(r.text),
                "body_preview": r.text[:300],
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
