from django.db import models

class ShopifyAccessToken(models.Model):
    shop_name = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    hmac_header = models.CharField(max_length=255)

class CustomerData(models.Model):
    customer_id = models.IntegerField()
    customer_first_name = models.TextField(max_length=255)
    customer_last_name = models.TextField(max_length=255)
    customer_email = models.CharField(max_length=255)
    customer_city = models.TextField(max_length=255)
    customer_country = models.TextField(max_length=255)