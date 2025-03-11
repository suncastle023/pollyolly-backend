# store/urls.py
from django.urls import path
from .views import BuyItemAPIView, get_items, refund_item_admin

urlpatterns = [
    path('buy/', BuyItemAPIView.as_view(), name='buy_item'),
    path('items/', get_items, name='get_items'),
    path('refund/admin/', refund_item_admin, name='refund_item_admin'),
]
