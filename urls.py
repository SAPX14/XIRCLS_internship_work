from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("landing/", views.landing, name="landing"),
    path("auth/", views.auth, name="auth"),
    path('access-token/', views.view_access_token, name="access_token"),
    path('webhook-handler/', views.webhook_handler, name="webhook"),
    path('better-reports/', views.customer_report_handler, name="report"),
]