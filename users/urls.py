from django.urls import path
from .views import GetNicknameView, CheckSessionView, get_csrf_token, UserInfoView


app_name = "users"

urlpatterns = [
    path("get-nickname/", GetNicknameView.as_view(), name="get_nickname"), 
    path("check-session/", CheckSessionView.as_view(), name="check_session"),  
    path("csrf-token/", get_csrf_token, name="check_session"),  
     path("get-user-info/", UserInfoView.as_view(), name="get-user-info"),
    
]
