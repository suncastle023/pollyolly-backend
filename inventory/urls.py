from django.urls import path
from .views import BuyItemAPIView, FeedPetAPIView, GiveWaterAPIView, PlayWithToyAPIView


app_name = 'inventory'


urlpatterns = [
    path("buy/", BuyItemAPIView.as_view(), name="buy_item"),
    path("feed/", FeedPetAPIView.as_view(), name="feed_pet"),
    path("water/", GiveWaterAPIView.as_view(), name="give_water"),
    path("play/", PlayWithToyAPIView.as_view(), name="play_with_toy"),
]
