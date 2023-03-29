from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from user_management.models import Comment, Like, Post
from user_management.permissions import IsOwnerOfObject
from user_management.serializers import TokenObtainPairSerializer, UserSerializer, CommentSerializer, LikeSerializer, \
    PostSerializer

User = get_user_model()


class EmailTokenObtainPairView(TokenObtainPairView):
    """Class for Token authentication"""

    serializer_class = TokenObtainPairSerializer


class UserModelViewSet(ModelViewSet):
    """signup for user"""

    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ('update', 'delete', 'retrieve'):
            return [IsAuthenticated(), IsOwnerOfObject()]
        elif self.action == 'list':
            return [IsAdminUser()]
        else:
            return [AllowAny()]


class UserPostsList(ListAPIView):
    """to get list of all posts related particular user"""

    serializer_class = PostSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(user_id=user_id)


class ChangePasswordView(APIView):
    """reset password"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.data)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data=form.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(UpdateAPIView):
    """to update user profile"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PostModelViewSet(ModelViewSet):
    """to create blog post, only auther can edit, retrieve and delete post """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        return Post.objects.filter(Q(visibility="PB") | Q(user_id=self.request.user.id))

    def list(self, request, *args, **kwargs):
        response = super(PostModelViewSet, self).list(request, *args, **kwargs)
        response.data = [{post.id: post.get_basic_details()} for post in self.get_queryset()]
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(PostModelViewSet, self).retrieve(request, *args, **kwargs)
        response.data = Post.objects.get(id=kwargs.get('pk')).get_basic_details()
        return response

    def update(self, request, *args, **kwargs):
        obj = Post.objects.filter(id=kwargs.get('pk'), user_id=self.request.user.id)
        if not obj:
            return Response(
                data={'detail': 'Only author can update the post'}, status=status.HTTP_400_BAD_REQUEST
            )
        user = request.data.pop('user')
        return super(PostModelViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = Post.objects.filter(id=kwargs.get('pk'), user_id=self.request.user.id)
        if not obj:
            return Response(
                data={'detail': 'Only author can delete the post'}, status=status.HTTP_400_BAD_REQUEST
            )
        deleted_post = super(PostModelViewSet, self).destroy(request, *args, **kwargs)
        deleted_post.data = {"details": "Post deleted successfully"}
        return deleted_post

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class LikeModelViewSet(ModelViewSet):
    """to like on particular post and count how much likes"""

    serializer_class = LikeSerializer
    queryset = Like.objects.all()


class CommentViewSet(ModelViewSet):
    """to comment on particular post"""
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class SearchAPIView(APIView):
    """user can search based on name, phone and email"""

    model = User
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_filters = self.search_params()
        user_objs = User.objects.filter(search_filters)
        data = []
        if user_objs:
            data = list(user_objs.values('id', 'name', 'email', 'phone', 'password'))
        return Response(data=data, status=status.HTTP_200_OK)

    def search_params(self):
        search_fields = Q()
        query_params = self.request.query_params
        name = query_params.get('name')
        email = query_params.get('email')
        phone = query_params.get('phone')
        if 'name' in query_params and name:
            search_fields = search_fields | Q(name__icontains=name)
        if 'email' in query_params and email:
            search_fields = search_fields | Q(email__icontains=email)
        if 'phone' in query_params and phone:
            search_fields = search_fields | Q(phone__icontains=phone)
        return search_fields
