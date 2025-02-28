# steps/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StepCount
from .serializers import StepCountSerializer
from datetime import date

class StepCountView(APIView):
    def get(self, request):
        """ 오늘의 걸음 수 조회 """
        today = date.today()
        step = StepCount.objects.filter(user=request.user, date=today).first()
        return Response({"date": today, "steps": step.steps if step else 0})

    def post(self, request):
        """ 걸음 수 저장 """
        print(f"📥 받은 요청 데이터: {request.data}")  # ✅ 요청 데이터 출력
        print(f"📥 요청 유저: {request.user}")  # ✅ 유저 정보 출력

        serializer = StepCountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            print(f"✅ 걸음 수 저장 완료: {serializer.data}")  # ✅ 저장 완료 로그
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(f"❌ 유효하지 않은 데이터: {serializer.errors}")  # ✅ 유효성 검사 실패 로그
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
