from django.urls import path
from .views import buy_item, get_items

urlpatterns = [
    path("buy/", buy_item, name="buy_item"),
    path("items/", get_items, name="get_items"),  # 🔹 모든 아이템 가져오기 API 추가
]
