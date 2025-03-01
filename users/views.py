from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response

User = get_user_model()

class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # ✅ 로그인된 사용자 정보

        return Response({
            "email": user.email,  # ✅ username 대신 email 사용
            "nickname": user.nickname,  # ✅ 닉네임 추가
            "level": user.level,  # ✅ 사용자 레벨 추가
            "phone_number": user.phone_number,  # ✅ 전화번호 추가
        })
    
    
# ✅ 세션 인증을 활용하여 닉네임 가져오기
class GetNicknameView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # ✅ 세션 기반 인증 적용
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 접근 가능

    def get(self, request):
        return JsonResponse({"nickname": request.user.nickname})

# ✅ 세션이 유지되고 있는지 확인하는 API
class CheckSessionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return JsonResponse({"message": "로그인 상태 유지 중"})


@ensure_csrf_cookie  # ✅ CSRF 쿠키 강제 설정
def get_csrf_token(request):
    csrf_token = get_token(request)  # ✅ CSRF 토큰 가져오기
    response = JsonResponse({"csrfToken": csrf_token})  # ✅ JSON 응답
    response.set_cookie("csrftoken", csrf_token)
    print(f"✅ CSRF 토큰 반환됨: {csrf_token}")  # 🔥 디버깅 로그 추가
    return response
