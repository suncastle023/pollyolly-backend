from django.urls import path
from .views import buy_item

urlpatterns = [
    path("buy/", buy_item, name="buy_item"),
]
