import json
import secrets
import base64
import logging
import requests
import httpx
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import List
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HubSpot App Credentials
CLIENT_ID = '3e185027-7d17-410e-80e6-8f18778eacd7'
CLIENT_SECRET = 'f1462a2e-87ac-44ee-b58c-67481c7a3f09'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
AUTHORIZATION_URL = 'https://app.hubspot.com/oauth/authorize'
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
SCOPES = "crm.objects.contacts.read%20crm.objects.contacts.write%20crm.schemas.contacts.read%20oauth"

async def authorize_hubspot(user_id, org_id):
    """Generates an authorization URL for HubSpot OAuth."""
    state_data = json.dumps({'state': secrets.token_urlsafe(32), 'user_id': user_id, 'org_id': org_id})
    encoded_state = base64.urlsafe_b64encode(state_data.encode()).decode()

    auth_url = (f'{AUTHORIZATION_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}'
                f'&scope={SCOPES}&state={encoded_state}')
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', state_data, expire=600)
    return auth_url

async def oauth2callback_hubspot(request: Request):
    """Handles OAuth2 callback from HubSpot."""
    if 'error' in request.query_params:
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
    
    code, encoded_state = request.query_params.get('code'), request.query_params.get('state')
    
    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode())
        user_id, org_id = state_data['user_id'], state_data['org_id']
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state encoding.")
    
    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or state_data['state'] != json.loads(saved_state)['state']:
        raise HTTPException(status_code=400, detail='State mismatch.')
    
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data={
            'grant_type': 'authorization_code', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI, 'code': code
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail='Failed to obtain access token.')
    
    token_data = response.json()
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(token_data), expire=600)
    await delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
    
    return HTMLResponse(content="""<html><script>window.close();</script></html>""")

async def refresh_hubspot_token(org_id, user_id, refresh_token):
    """Refreshes HubSpot access token using the refresh token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data={
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': refresh_token
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        logger.info(f"HubSpot Token Refresh Response: {response.text}")  # Log full response

    if response.status_code != 200:
        logger.error(f"Failed to refresh HubSpot token: {response.text}")
        raise HTTPException(status_code=400, detail="Failed to refresh token.")

    token_data = response.json()

    # Log the new access & refresh token
    logger.info(f"New Access Token: {token_data.get('access_token')}")
    logger.info(f"New Refresh Token: {token_data.get('refresh_token')}")

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(token_data), expire=600)
    return token_data

async def get_hubspot_credentials(user_id, org_id):
    """Fetches HubSpot credentials, refreshing the token if needed."""
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found.")

    credentials = json.loads(credentials)
    access_token, refresh_token = credentials.get("access_token"), credentials.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token missing.")

    # Check if token needs refreshing (HubSpot tokens typically last 30 minutes)
    if "expires_in" in credentials:
        expires_in = credentials["expires_in"]
        if expires_in < 60:  # Refresh if less than 1 min remaining
            credentials = await refresh_hubspot_token(org_id, user_id, refresh_token)

    return credentials

def create_integration_item_metadata_object(contact):
    """Transforms HubSpot contact data into IntegrationItem format."""
    properties = contact.get("properties", {})
    firstname = properties.get("firstname", "") or ""
    lastname = properties.get("lastname", "") or ""

    # If both are empty, name will be an empty string
    name = f"{firstname} {lastname}".strip() or firstname or lastname

    return IntegrationItem(
        id=contact.get("id"),
        hs_object_id=properties.get("hs_object_id"),
        name=name,
        email=properties.get("email"),
        creation_time=properties.get("createdate"),
        last_modified_time=properties.get("lastmodifieddate")
    )

async def get_items_hubspot(credentials: str) -> List[IntegrationItem]:
    """Fetches contacts from HubSpot and returns them as IntegrationItem objects."""
    credentials = json.loads(credentials)
    access_token, refresh_token = credentials.get("access_token"), credentials.get("refresh_token")
    
    if not access_token:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "limit": 100,
        "properties": "firstname,lastname,email,createdate,lastmodifieddate"
    }
    contacts = []

    def fetch_contacts():
        """Helper function to make the API request."""
        return requests.get(HUBSPOT_CONTACTS_URL, headers=headers, params=params)

    try:
        while True:
            response = fetch_contacts()
            
            if response.status_code == 401 and refresh_token:
                logger.info("Access token expired, attempting refresh...")
                new_credentials = await refresh_hubspot_token(credentials["org_id"], credentials["user_id"], refresh_token)
                
                if not (new_access_token := new_credentials.get("access_token")):
                    logger.error("Failed to refresh access token. Unauthorized access.")
                    raise HTTPException(status_code=401, detail="Unauthorized: Token refresh failed.")
                
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = fetch_contacts()
                
                if response.status_code == 401:
                    logger.error("New access token is also unauthorized.")
                    raise HTTPException(status_code=401, detail="Unauthorized: Access token expired or invalid.")
            
            if response.status_code != 200:
                logger.error(f"HubSpot API request failed: {response.status_code}, Response: {response.text}")
                break
            
            data = response.json()
            contacts.extend([create_integration_item_metadata_object(c) for c in data.get("results", [])])
            
            if not (paging := data.get("paging", {}).get("next", {}).get("after")):
                break
            params["after"] = paging  # Continue pagination
        
        return contacts
    except Exception as e:
        logger.exception(f"Error while fetching contacts from HubSpot: {e}")
        return []