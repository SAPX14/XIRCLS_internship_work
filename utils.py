import requests
from django.shortcuts import *
from .models import *

def token(request):

    # After the user authorizes the application, Shopify will redirect here
    shop = request.GET.get('shop')
    code = request.GET.get('code')

    # Make a request to Shopify to exchange the authorization code for an access token
    api_key = "0e343bae54184399236ba1e577c6f39d"
    api_secret = "50784e16dd6d19d559fc1fcbf2bd81ce"
    access_token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        'client_id': api_key,
        'client_secret': api_secret,
        'code': code
    }
    response = requests.post(access_token_url, data=payload)
    access_token = response.json().get('access_token')
    return access_token