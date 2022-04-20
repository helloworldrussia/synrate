from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class SynrateUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "Пользователь с данным именем уже существует.",
        },
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(null=True, blank=True, max_length=300, verbose_name='Имя')
    last_name = models.CharField(null=True, blank=True, max_length=300, verbose_name='Фамилия')
    subscribe = models.TextField(null=True, blank=True)
    subscribed = models.BooleanField(null=False, default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    def __str__(self):
        return self.username

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username=username,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user