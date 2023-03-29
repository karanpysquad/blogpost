from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    PHONE_NUMBER_REGEX = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    username = None
    first_name = None
    last_name = None

    name = models.CharField(verbose_name=_('Full Name'), max_length=150)
    email = models.EmailField(verbose_name=_('Email Address'), unique=True, null=False)
    phone = models.CharField(
        verbose_name=_('Phone Number'), max_length=17, null=True, blank=True, validators=[PHONE_NUMBER_REGEX]
    )
    profile_picture = models.ImageField(
        verbose_name=_('Profile Picture'), upload_to='media/profile_pictures', null=True, blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Post(models.Model):
    POST_VISIBILITY_CHOICES = (
        ('PB', 'Public'),
        ('PR', 'Private')
    )
    user = models.ForeignKey(verbose_name='User', to=User, on_delete=models.CASCADE, related_name='posts', blank=True)
    caption = models.TextField(verbose_name='Caption', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Posted On', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated On', auto_now=True)
    visibility = models.CharField(
        verbose_name='Post Visibility', default='PB', choices=POST_VISIBILITY_CHOICES, max_length=2
    )
    post = models.FileField(verbose_name="Post", upload_to="media/posts")

    class Meta:
        db_table = 'post'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return str(self.id)

    @property
    def get_post_likes(self):
        return self.post_likes.count()

    @property
    def get_post_comment(self):
        return self.post_comment.values_list('comment', flat=True)

    def get_basic_details(self):
        user = self.user
        return {
            "id": self.id,
            "user": {
                "id": user.id,
                "username": user.username,
            },
            "caption": self.caption,
            "visibility": dict(self.POST_VISIBILITY_CHOICES).get(self.visibility),
            "post_url": self.post.url,
            'post_likes': self.get_post_likes,
            "post_comment": self.get_post_comment
        }


class Like(models.Model):
    post = models.ForeignKey(verbose_name='Post', to=Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(verbose_name='User', to=User, on_delete=models.CASCADE, related_name='users')
    created_ad = models.DateTimeField(verbose_name="Liked On", auto_now_add=True)

    class Meta:
        db_table = 'post_like'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        unique_together = ('post', 'user',)

    def __str__(self):
        return str(self.id)


class Comment(models.Model):
    post = models.ForeignKey(verbose_name='Post', to=Post, on_delete=models.CASCADE, related_name='post_comment')
    user = models.ForeignKey(verbose_name='User', to=User, on_delete=models.CASCADE, related_name='user_comment')
    comment = models.TextField(max_length=250, blank=True)
    created_ad = models.DateTimeField(verbose_name="Comment On", auto_now_add=True)

    class Meta:
        db_table = 'post_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        unique_together = ('post', 'user',)

    def __str__(self):
        return str(self.id)
