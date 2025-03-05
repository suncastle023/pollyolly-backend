from django.urls import path
from .views import PetCreateView, PetListView, MyActivePetAPIView

app_name = 'pet'

urlpatterns = [
    path('create/', PetCreateView.as_view(), name='create_pet'),
    path('mypetList/', PetListView.as_view(), name='mypet_list'),
    path('petinfo/', MyActivePetAPIView.as_view(), name='my_pet_info'),
    

]