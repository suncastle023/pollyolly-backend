from django.urls import path
from .views import (
    SendFriendRequestView,
    ReceivedFriendRequestsView,
    RespondFriendRequestView,
    FriendListView, 
    RemoveFriendView, 
    FriendPetListView
)

app_name = 'friend'

urlpatterns = [
    path("", FriendListView.as_view(), name="friend-list"),  # 친구 목록 조회
    path("<int:friend_id>/", RemoveFriendView.as_view(), name="remove-friend"),  # 친구 삭제
    path("<int:friend_id>/pets/", FriendPetListView.as_view(), name="friend-pets"),  # 친구의 펫 조회
    path("request/", SendFriendRequestView.as_view(), name="send-friend-request"),
    path("requests/", ReceivedFriendRequestsView.as_view(), name="received-friend-requests"),
    path("request/respond/<int:request_id>/", RespondFriendRequestView.as_view(), name="respond-friend-request"),
    path("remove/<int:friend_id>/", RemoveFriendView.as_view(), name="remove-friend"), 

]
