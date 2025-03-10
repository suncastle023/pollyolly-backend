from django.urls import path
from .views import BuyItemAPIView, FeedPetAPIView, GiveWaterAPIView, PlayWithToyAPIView, GetInventoryAPIView

app_name = 'inventory'

urlpatterns = [
    path("buy/", BuyItemAPIView.as_view(), name="buy_item"),
    path("feed/", FeedPetAPIView.as_view(), name="feed_pet"),  # 일반 & 프리미엄 사료 포함
    path("water/", GiveWaterAPIView.as_view(), name="give_water"),  # 일반 & 프리미엄 물 포함
    path("play/", PlayWithToyAPIView.as_view(), name="play_with_toy"),  # 장난감 종류별 구분
    path("get-inventory/", GetInventoryAPIView.as_view(), name="get_inventory"),
]
