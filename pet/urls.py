from django.urls import path
from .views import PetCreateView, PetListView, PetLevelUpView

app_name = 'pet'

urlpatterns = [
    path('create/', PetCreateView.as_view(), name='create_pet'),
    path('mypetList/', PetListView.as_view(), name='mypet_list'),
    path('<int:pet_id>/levelup/', PetLevelUpView.as_view(), name='level_up_pet'),
]