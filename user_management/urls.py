from django.urls import path
from rest_framework.routers import DefaultRouter

from user_management.views import EmailTokenObtainPairView, UserModelViewSet, SearchAPIView, ChangePasswordView, \
    UserProfileUpdateView, PostModelViewSet, LikeModelViewSet, CommentViewSet, UserPostsList

router = DefaultRouter()

router.register('user', UserModelViewSet)
router.register('blog/post', PostModelViewSet)
router.register('blog/like', LikeModelViewSet)
router.register('blog/comment', CommentViewSet)

urlpatterns = [
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('reset_password/', ChangePasswordView.as_view(), name='reset'),
    path('update-profile/', UserProfileUpdateView.as_view(), name='update'),
    path('profile-view/<int:user_id>/', UserPostsList.as_view(), name='profile'),
    path('search/', SearchAPIView.as_view(), name='user_search'),
] + router.urls
