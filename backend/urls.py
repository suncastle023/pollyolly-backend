from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path("users/", include("users.urls")), 
    path('pet/', include('pet.urls')), 
    path('steps/', include('steps.urls')), 
    
]
