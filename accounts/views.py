from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSignupSerializer, UserLoginSerializer
from django.conf import settings
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator


User = get_user_model()

# ✅ 로그인 홈 화면 (이메일 로그인 & 카카오 로그인 버튼)
def login_home(request):
    return render(request, "accounts/login_home.html")

class CheckNicknameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        nickname = request.GET.get("nickname")
        if not nickname:
            return Response({"error": "닉네임을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(nickname=nickname).exists():
            return Response({"error": "이미 사용 중인 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)

class CheckEmailDuplicateView(APIView):
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return Response({"error": "이메일을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "사용 가능한 이메일입니다!"}, status=status.HTTP_200_OK)


class SaveKakaoNicknameView(APIView):
    def post(self, request):
        email = request.data.get("email")  # ✅ request.POST에서 request.data로 변경 (DRF 방식)
        nickname = request.data.get("nickname")

        if User.objects.filter(nickname=nickname).exists():
            return Response({"error": "이미 사용 중인 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 이메일로 사용자 찾기
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ 닉네임 저장
        user.nickname = nickname
        user.save()

        # ✅ 로그인 처리
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        # ✅ 세션 저장 강제
        request.session["user_id"] = user.id
        request.session.save()

        # ✅ 세션 ID 가져오기
        sessionid = request.session.session_key

        response = Response({
            "status": "login_success",
            "message": "로그인 성공!",
            "email": email,
            "nickname": user.nickname,
            "sessionid": sessionid,  # ✅ 세션 ID 포함
        }, status=status.HTTP_200_OK)

        # ✅ 세션 쿠키 강제 설정
        response.set_cookie(
            "sessionid", sessionid,
            httponly=True, samesite="None", secure=False  # HTTPS 환경에서는 secure=True 설정
        )

        print(f"✅ Set-Cookie: sessionid={sessionid}")  # 로그 확인
        return response


# ✅ 카카오 로그인 
class KakaoLoginView(APIView):
    def get(self, request):
        kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.SOCIAL_AUTH_KAKAO_KEY}&redirect_uri={settings.SOCIAL_AUTH_KAKAO_REDIRECT_URI}&response_type=code"
        return JsonResponse({"auth_url": kakao_auth_url})



# ✅ 카카오 로그인 콜백 처리
class KakaoLoginCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        # ✅ 1. 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.SOCIAL_AUTH_KAKAO_KEY,
            "client_secret": settings.SOCIAL_AUTH_KAKAO_SECRET,
            "redirect_uri": settings.SOCIAL_AUTH_KAKAO_REDIRECT_URI,
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(token_url, data=data, headers=headers)
        token_json = token_response.json()

        if "access_token" not in token_json:
            return JsonResponse({"error": "카카오 로그인 실패"}, status=400)

        access_token = token_json["access_token"]

        # ✅ 2. 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info_json = user_info_response.json()

        kakao_id = str(user_info_json.get("id"))
        kakao_account = user_info_json.get("kakao_account", {})
        email = kakao_account.get("email", None)
        kakao_nickname = kakao_account.get("profile", {}).get("nickname", None)

        if email is None:
            email = f"kakao_{kakao_id}@noemail.com"

        # ✅ 3. 기존 유저 확인
        user, created = User.objects.get_or_create(email=email, defaults={"kakao_id": kakao_id})

        if not user.kakao_id:
            user.kakao_id = kakao_id
            user.save()

        # ✅ 4. 닉네임이 없는 경우 추가 정보 입력 필요
        if not user.nickname:
            return JsonResponse({
                "status": "additional_info_required",
                "message": "추가 정보 입력이 필요합니다.",
                "email": email,
                "kakao_nickname": kakao_nickname
            })

        # ✅ 5. 로그인 처리 후 앱으로 닉네임과 함께 반환
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

         # ✅ 세션 ID 가져오기
        sessionid = request.session.session_key

        # ✅ 세션 ID를 JSON 응답에 포함
        return JsonResponse({
            "status": "login_success",
            "message": "로그인 성공!",
            "email": email,
            "nickname": user.nickname,
            "sessionid": sessionid  # ✅ 세션 ID 추가
        })

# ✅ 일반 회원가입
class SignupView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")
        nickname = request.data.get("nickname")  # ✅ 닉네임 받기

        if not email or not password or not phone_number or not nickname:
            return Response({"error": "모든 필드를 입력해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(nickname=nickname).exists():
            return Response({"error": "이미 사용 중인 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(email=email, phone_number=phone_number, nickname=nickname)
        user.set_password(password)  # ✅ 비밀번호 암호화 저장
        user.save()

        return Response({"message": "회원가입 성공!"}, status=status.HTTP_201_CREATED)


# ✅ 일반 로그인
class LoginView(APIView):
    def get(self, request):
        return Response({"error": "로그인은 POST 요청으로만 가능합니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            request.session["user_id"] = user.id
            request.session.save()

            session_id = request.session.session_key
            response = JsonResponse({
                "message": "로그인 성공!",
                "user_id": user.id,
                "nickname": user.nickname,
            }, json_dumps_params={"ensure_ascii": False}, status=status.HTTP_200_OK)

            response.set_cookie(
                key="sessionid",
                value=session_id,
                httponly=True,
                samesite="None",
                secure=False
            )

            return response

        return JsonResponse(
            {"error": "이메일 또는 비밀번호가 잘못되었습니다."},
            json_dumps_params={"ensure_ascii": False}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    
# ✅ 로그아웃
class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)  # ✅ CSRF 보호 적용 (토큰 필요)
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "로그인이 필요합니다."}, status=403)

        logout(request)
        request.session.flush()

        response = JsonResponse({"message": "로그아웃 성공!"}, status=200)
        response.delete_cookie("sessionid")  # ✅ 세션 쿠키 삭제
        response.delete_cookie("csrftoken")  # ✅ CSRF 토큰 삭제
        return response