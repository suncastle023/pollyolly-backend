from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friend
from .serializers import FriendSerializer, FriendPetSerializer, FriendRequestSerializer, FriendRequestResponseSerializer, FriendSerializer
from pet.models import Pet
import json

User = get_user_model()

# ✅ 친구 목록 조회
class FriendListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)


# ✅ 친구 요청 보내기 (디버깅 추가)
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            receiver_email = request.data.get("friend_email", "").strip().lower()  # ✅ 이메일 소문자로 변환 및 공백 제거

            # ✅ [DEBUG] 서버에서 받은 이메일 확인
            print(f"📌 [DEBUG] 요청된 친구 이메일: {receiver_email}")

            if not receiver_email:
                return Response({"error": "이메일이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ DB에서 이메일 검색 (대소문자 무시)
            try:
                receiver = User.objects.get(email__iexact=receiver_email)
                print(f"✅ [DEBUG] 찾은 사용자: {receiver.email}, 닉네임: {receiver.nickname}")
            except User.DoesNotExist:
                print(f"❌ [DEBUG] DB에서 사용자를 찾을 수 없음: {receiver_email}")
                return Response(
                    {"error": "해당 이메일의 사용자를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            sender = request.user

            # ✅ 이미 친구인지 확인
            if Friend.objects.filter(user=sender, friend=receiver).exists():
                return Response({"error": "이미 친구입니다."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ 이미 보낸 친구 요청이 있는지 확인
            if FriendRequest.objects.filter(sender=sender, receiver=receiver, status="pending").exists():
                return Response({"error": "이미 보낸 친구 요청이 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ 친구 요청 생성
            FriendRequest.objects.create(sender=sender, receiver=receiver)
            return Response(
                {"message": "친구 요청이 성공적으로 전송되었습니다."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print(f"❌ [DEBUG] 서버 오류 발생: {str(e)}")
            return Response({"error": "서버 내부 오류 발생"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ 받은 친구 요청 목록 조회
class ReceivedFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        requests = FriendRequest.objects.filter(receiver=self.request.user, status="pending")
        return requests
    


# ✅ 친구 요청 수락/거절
class RespondFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        request_id = kwargs.get("request_id")
        try:
            friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user, status="pending")
        except FriendRequest.DoesNotExist:
            return Response({"error": "유효하지 않은 친구 요청입니다."}, status=status.HTTP_404_NOT_FOUND)

        status_choice = request.data.get("status")
        if status_choice not in ["accepted", "rejected"]:
            return Response({"error": "잘못된 상태값입니다. (accepted / rejected만 가능)"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = status_choice
        friend_request.save()

        if status_choice == "accepted":
            Friend.objects.create(user=request.user, friend=friend_request.sender)
            Friend.objects.create(user=friend_request.sender, friend=request.user)
            return Response({"message": "친구 요청을 수락하였습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "친구 요청을 거절하였습니다."}, status=status.HTTP_200_OK)



# ✅ 친구 삭제 API
class RemoveFriendView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        friend_id = kwargs.get("friend_id")
        try:
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            return Response({"error": "해당 유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 친구 관계 삭제
        Friend.objects.filter(user=request.user, friend=friend).delete()
        Friend.objects.filter(user=friend, friend=request.user).delete()  # 상호 삭제
        return Response({"message": "친구가 삭제되었습니다."}, status=status.HTTP_200_OK)


# ✅ 친구의 펫 목록 조회 API (친구인 경우만 허용)
class FriendPetListView(generics.ListAPIView):
    serializer_class = FriendPetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friend_id = self.kwargs.get("friend_id")

        # ✅ 친구 관계 확인 (user와 friend_id가 친구인지 체크)
        if not Friend.objects.filter(user=user, friend__id=friend_id).exists():
            return Pet.objects.none()  # 친구가 아니면 빈 데이터 반환
        
        return Pet.objects.filter(owner_id=friend_id)  # 친구의 펫 리스트 반환

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # ✅ 반환할 데이터가 없으면 404 반환
        if not serializer.data:
            return Response({"error": "친구가 없거나 키우는 펫이 없습니다."}, status=404)

        return Response(serializer.data, status=200)