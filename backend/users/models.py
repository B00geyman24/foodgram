from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    """Пользовательские роли."""

    ADMIN = 'admin', 'Админ'
    USER = 'user', 'Пользователь'


class User(AbstractUser):
    """Кастомная модель пользователя."""

    first_name = models.CharField(
        verbose_name='Имя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=UserRole.choices,
        default=UserRole.USER
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} - {self.role}'

    @property
    def is_admin(self):
        """Проверка на роль администратора."""
        return self.role == UserRole.ADMIN or self.is_superuser
