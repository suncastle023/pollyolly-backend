from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StepCount
from .serializers import StepCountSerializer

class StepCountView(generics.CreateAPIView):
    serializer_class = StepCountSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        step_count = request.data.get("step_count")

        if not step_count:
            return Response({"error": "걸음 수를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        step_record, created = StepCount.objects.update_or_create(
            user=request.user, date=request.data.get("date"),
            defaults={"step_count": step_count}
        )

        return Response(StepCountSerializer(step_record).data, status=status.HTTP_201_CREATED)
