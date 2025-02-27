from django.urls import path
from .views import StepCountView

app_name = 'steps'

urlpatterns = [
    path('steps/', StepCountView.as_view(), name='step_count'),
]
