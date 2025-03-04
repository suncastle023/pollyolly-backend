import random
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
        pet_name = request.data.get("name", "새로운 펫")
        pet_type = request.data.get("pet_type")  # ✅ 사용자가 선택한 pet_type

        if not pet_type or pet_type not in Pet.PET_TYPES:
            return Response({"error": "유효하지 않은 펫 유형입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 사용자가 선택한 pet_type의 breed 중 랜덤 선택
        breed = random.choice(Pet.PET_TYPES[pet_type])

        # ✅ 선택한 pet_type과 breed를 사용하여 펫 생성
        pet = Pet.objects.create(owner=user, name=pet_name, pet_type=pet_type, breed=breed)
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

            print(f"🚀 {pet.name} 레벨업 실행 (현재 레벨: {pet.level}, 경험치: {pet.experience})")
            pet.level_up()
            pet.save()
            print(f"✅ 레벨업 완료! 새로운 레벨: {pet.level}, 경험치: {pet.experience}")

            return Response({"message": f"{pet.name}의 레벨이 {pet.level}이 되었습니다!"}, status=status.HTTP_200_OK)

        except Pet.DoesNotExist:
            return Response({"error": "해당 반려동물을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)



class MyActivePetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 레벨이 10 미만인 펫 중 하나 가져오기
        pet = Pet.objects.filter(owner=request.user, level__lt=10).first()  # ✅ owner로 수정
        if not pet:
            return Response({"message": "현재 키우는 펫이 없습니다."}, status=404)

        data = {
            "id": pet.id,
            "name": pet.name,
            "breed": pet.breed,  
            "pet_type": pet.pet_type,  
            "level": pet.level,
            "experience": pet.experience,
            'health':pet.health,
        }
        return Response(data)

