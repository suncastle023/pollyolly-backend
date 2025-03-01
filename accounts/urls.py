from django.urls import path
from .views import SignupView, LoginView, LogoutView, CheckNicknameView, SaveKakaoAddinfoView
from .views import login_home, KakaoLoginView, KakaoLoginCallbackView, CheckEmailDuplicateView

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login_home'),  
    path('loginhome/', login_home, name='login_home'),  
    path('kakao/login/', KakaoLoginView.as_view(), name='kakao_login'),  
    path('kakao/login/callback/', KakaoLoginCallbackView.as_view(), name='kakao_callback'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('check-nickname/', CheckNicknameView.as_view(), name='check_nickname'),
    path('kakao/save-additional-info/', SaveKakaoAddinfoView.as_view(), name='save_kakao_nickname'),
     path("check-email/", CheckEmailDuplicateView.as_view(), name="check_email"),


]
