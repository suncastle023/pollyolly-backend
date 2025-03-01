from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pet
from .serializers import PetSerializer
from rest_framework.views import APIView

class PetCreateView(generics.CreateAPIView):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not hasattr(user, "level"):
            return Response({"error": "사용자의 레벨 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        level = user.level 

        # 사용자가 선택할 수 있는 펫 리스트 가져오기
        pet_type, breed = Pet.get_random_pet(level)

        if not pet_type or not breed:
            return Response({"error": "선택 가능한 펫이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 펫 생성
        pet = Pet.objects.create(owner=user, name=request.data.get("name", "새로운 펫"), pet_type=pet_type, breed=breed)
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PetListView(generics.ListAPIView):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pets = Pet.objects.filter(owner=self.request.user)
        for pet in pets:
            pet.reduce_experience_over_time()  # ✅ 조회 시 자동으로 체력 감소 반영
        return pets
    
class PetLevelUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pet_id):
        try:
            pet = Pet.objects.get(id=pet_id, owner=request.user)
            if pet.level >= 10:
                return Response({"message": "최대 레벨(10)에 도달했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            pet.level_up()
            return Response({"message": f"{pet.name}의 레벨이 {pet.level}이 되었습니다!"}, status=status.HTTP_200_OK)
        except Pet.DoesNotExist:
            return Response({"error": "해당 반려동물을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
class MyActivePetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 레벨이 10 미만인 펫 중 하나 가져온다고 가정
        pet = Pet.objects.filter(user=request.user, level__lt=10).first()
        if not pet:
            return Response({"message": "현재 키우는 펫이 없습니다."}, status=404)

        data = {
            "id": pet.id,
            "name": pet.name,
            "level": pet.level,
            "experience": pet.experience,
        }
        return Response(data)
