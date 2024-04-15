import requests
from main import *
def get_long_lived_access_token(app_id, app_secret, short_lived_token):
    """
    Exchange a short-lived token for a long-lived token.

    Args:
    app_id (str): Your Facebook App ID.
    app_secret (str): Your Facebook App Secret.
    short_lived_token (str): The short-lived access token obtained via Facebook Login.

    Returns:
    str: Long-lived access token or an error message.
    """
    url = "https://graph.facebook.com/v14.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        return data['access_token']
    else:
        return "Error obtaining long-lived token: " + data.get('error', {}).get('message', 'No error message provided.')

# Usage example:
if __name__ == "__main__":
    APP_ID = '1413214649339539'  # Replace with your Facebook App ID
    APP_SECRET = 'b803cf8064d333684504f6887588058a'  # Replace with your Facebook App Secret
    SHORT_LIVED_TOKEN = access_token  # Replace with your short-lived access token
    
    long_lived_token = get_long_lived_access_token(APP_ID, APP_SECRET, SHORT_LIVED_TOKEN)
    print("Long-Lived Token:", long_lived_token)
