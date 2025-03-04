from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friend
from pet.models import Pet  

User = get_user_model()

# ✅ 친구 목록 조회 Serializer
class FriendSerializer(serializers.ModelSerializer):
    friend_id = serializers.IntegerField(source="friend.id", read_only=True)
    friend_nickname = serializers.CharField(source="friend.nickname", read_only=True)
    friend_level = serializers.IntegerField(source="friend.level", read_only=True)

    class Meta:
        model = Friend
        fields = ["friend_id", "friend_nickname", "friend_level"]

# ✅ 친구 추가 Serializer
class FriendCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ["friend"]

    def validate(self, data):
        user = self.context["request"].user
        friend = data["friend"]
        if user == friend:
            raise serializers.ValidationError("자기 자신을 친구로 추가할 수 없습니다.")
        if Friend.objects.filter(user=user, friend=friend).exists():
            raise serializers.ValidationError("이미 친구로 추가된 사용자입니다.")
        return data


# ✅ 친구의 펫 목록 조회 Serializer
class FriendPetSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Pet
        fields = ["name", "level", "pet_type", "breed", "status"]
    
    def get_status(self, obj):
        if obj.health > 50:
            return "건강함"
        elif obj.health > 30:
            return "주의 필요"
        else:
            return "위험"
        


# ✅ 친구 요청 Serializer
class FriendRequestSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True)  # ✅ 보낸 사람 이메일 추가
    sender_nickname = serializers.CharField(source="sender.nickname", read_only=True)  # ✅ 보낸 사람 닉네임 추가
    sender_level = serializers.IntegerField(source="sender.level", read_only=True)  # ✅ 보낸 사람 레벨 추가
    receiver_email = serializers.EmailField(write_only=True)  # ✅ 친구 요청 보낼 때만 사용

    class Meta:
        model = FriendRequest
        fields = ["id", "sender_email", "sender_nickname", "sender_level", "status", "receiver_email"]


    def validate(self, data):
        sender = self.context["request"].user
        receiver_email = data["receiver_email"]

        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("해당 이메일의 사용자를 찾을 수 없습니다.")

        if sender == receiver:
            raise serializers.ValidationError("자기 자신에게 친구 요청을 보낼 수 없습니다.")

        if FriendRequest.objects.filter(sender=sender, receiver=receiver, status="pending").exists():
            raise serializers.ValidationError("이미 보낸 친구 요청이 있습니다.")

        if Friend.objects.filter(user=sender, friend=receiver).exists():
            raise serializers.ValidationError("이미 친구로 등록된 사용자입니다.")

        data["receiver"] = receiver
        return data

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver = validated_data["receiver"]
        return FriendRequest.objects.create(sender=sender, receiver=receiver)

# ✅ 친구 요청 수락/거절 Serializer
class FriendRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["status"]
