from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AuthUserManager
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.db import models


class UserManager(AuthUserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('sex', 'm')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    sex = models.CharField(
            max_length=1,
            choices=(
                ('f', 'female'),
                ('m', 'male'),
            ))

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    website_url = models.URLField(blank=True)


def on_post_save_for_user(sender, **kwargs):
    if kwargs['created']:
        # 가입시기
        user = kwargs['instance']

        # 환영 이메일 보내기
        send_mail(
            '환영합니다.',
            'Here is the message.',
            'me@askcompany.kr',
            [user.email],
            fail_silently=False,
        )

post_save.connect(on_post_save_for_user, sender=settings.AUTH_USER_MODEL)


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


def on_user_logged_in(sender, request, user, **kwargs):
    user.is_user_logged_in = True

user_logged_in.connect(on_user_logged_in)

