# steps/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StepCount
from .serializers import StepCountSerializer
from datetime import date
from django.contrib.auth import get_user

class StepCountView(APIView):
    def get(self, request):
        """ 오늘의 걸음 수 조회 """
        today = date.today()
        step = StepCount.objects.filter(user=request.user, date=today).first()
        return Response({"date": today, "steps": step.steps if step else 0})

    def post(self, request):
        user = get_user(request)  # ✅ LazyObject를 실제 CustomUser 객체로 변환

        serializer = StepCountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # ✅ 변환된 user 객체 저장
            #print(f"✅ 걸음 수 저장 완료: {serializer.data}")  # ✅ 저장 완료 로그
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(f"❌ 유효하지 않은 데이터: {serializer.errors}")  # ✅ 유효성 검사 실패 로그
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)