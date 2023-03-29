from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer
from django.core.validators import RegexValidator

from user_management.models import Post, Like, Comment


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD


class UserSerializer(serializers.ModelSerializer):
    PASSWORD_REGEX = RegexValidator(
        regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$',
        message="Password must be at least 8 characters long and contain at least one digit, one lowercase letter, "
                "and one uppercase letter."
    )
    password = serializers.CharField(max_length=128, write_only=True, validators=[PASSWORD_REGEX])

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'phone', 'profile_picture', 'password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(user.password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserSerializer, self).update(instance, validated_data)
        password = validated_data.get('password', None)
        if password is not None:
            user.set_password(raw_password=password)
            user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'post', 'caption', 'visibility', 'user')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post', 'user')

    def get_unique_together_validators(self):
        error = super(LikeSerializer, self).get_unique_together_validators()
        error[0].message = "You have already liked this post..!"
        return error


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'user', 'comment')
