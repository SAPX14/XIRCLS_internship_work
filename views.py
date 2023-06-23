from django.shortcuts import redirect, render
import requests
from .models import *
import json
import hmac
import hashlib
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import time 
from functools import reduce
import pandas as pd
from collections import Counter
from itertools import chain
import tracemalloc

# pass@123


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def landing(request):
    print("Hello")
    shop = request.GET.get("shop")
    api_key = "fc773424dc7d98b4ec5b17f8009fd3f7"
    access_scopes = (
        "read_products,write_products,read_customers,write_customers, read_orders"
    )
    redirect_uri = "https://c57a-110-226-177-80.ngrok-free.app/auth"
    return redirect(
        f"https://{shop}/admin/oauth/authorize?client_id={api_key}&scope={access_scopes}&redirect_uri={redirect_uri}"
    )


def auth(request):
    # After the user authorizes the application, Shopify will redirect here
    shop = request.GET.get("shop")
    code = request.GET.get("code")
    hmac_header = request.GET.get("hmac")

    # Make a request to Shopify to exchange the authorization code for an access token
    api_key = "fc773424dc7d98b4ec5b17f8009fd3f7"
    api_secret = "e86d55481860774472e5ca3f9689ef87"
    access_token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {"client_id": api_key, "client_secret": api_secret, "code": code}
    response = requests.post(access_token_url, data=payload)

    if response.status_code == 200:
        # Successfully obtained the access token
        access_token = response.json().get("access_token")
        shopify_access_token = ShopifyAccessToken(
            shop_name=shop, access_token=access_token, hmac_header=hmac_header
        )
        shopify_access_token.save()
        try:
            """code snippet for webhook"""
            webhook_url = f"https://{shop}/admin/api/2023-04/webhooks.json"
            webhook_payload = {
                "webhook": {
                    "topic": "orders/create",
                    "address": "https://c57a-110-226-177-80.ngrok-free.app/webhook-handler/",
                    "format": "json",
                }
            }
            webhook_headers = {
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            webhook_response = json.loads(
                requests.post(
                    webhook_url,
                    data=json.dumps(webhook_payload),
                    headers=webhook_headers,
                ).text
            )
            print(webhook_response)

        except:
            print("error")
        return HttpResponse(access_token)

    else:
        # Failed to obtain the access token
        return HttpResponse("Authorization failed!")


def view_access_token(request):
    token = ShopifyAccessToken.objects.latest("created_at")
    return render(request, "access_token.html", {"access_token": token.access_token})


@csrf_exempt
def webhook_handler(request):
    # Verify the webhook request
    # (You can add additional validation here if needed)
    data = request.body
    print(data)
    message = {"message": "working"}
    return JsonResponse(message, status=200)


# def register_webhook_view(request):
#     # Call the register_webhook function
#     shopify_webhook(request)

#     # Render a response or redirect as needed
#     return render(request, "registration_success.html")


def customer_report_handler(request):
    tracemalloc.start()
    start = time.perf_counter()
    shop = ShopifyAccessToken.objects.get().shop_name
    access_token = ShopifyAccessToken.objects.get(shop_name=shop).access_token
    
    better_report_customer_url = f"https://{shop}/admin/api/2023-04/customers.json"
    
    better_report_customer_headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    better_report_customer_response = json.loads(
        requests.get(
            better_report_customer_url, headers=better_report_customer_headers
        ).text
    )
    
    customer_data = better_report_customer_response["customers"]
    """ method 1 """
    # country_count = defaultdict(int)
    # for customer in customer_data:
    #     addresses = customer["addresses"]
    #     for address in addresses:
    #         country = address["country"]
    #         country_count[country] += 1 

    # country_count = dict(sorted(country_count.items()))

    """ method 2 """
    addresses = []
    for customer in customer_data:
        addresses.extend(customer['addresses'])
    df = pd.DataFrame(addresses)
    country_count = df['country'].value_counts().to_dict()
    
    """ method 3 """
    # addresses = chain.from_iterable(map(lambda customer: customer.get('addresses', []), customer_data))
    # country_count = dict(Counter(map(lambda address: address['country'], addresses)))

    """ method 4 """
    # country_count = reduce(
    #     lambda counts, customer: {
    #         **counts,
    #         **{address['country']: counts.get(address['country'], 0) + 1 for address in customer.get('addresses', [])}
    #     },
    #     customer_data,
    #     {}
    # )

    name = "Pasha"
    filtered_names = [customer for customer in customer_data if customer["first_name"] == name]

    context = {"customer_data":customer_data, "country_count":country_count, "filtered_names":filtered_names}
    end = time.perf_counter()
    print(f"**************{end-start}***************")    
    print(tracemalloc.get_traced_memory())
    tracemalloc.stop()
    # return HttpResponse(f"Customer list retrieved successfully\n{customer_first_name}")
    return render(request, "customer_data.html", context)
