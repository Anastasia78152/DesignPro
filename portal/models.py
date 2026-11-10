from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Категории дизайн-проектов (например, Кухня, Спальня, Офис)."""
    name = models.CharField('Название категории', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Расширенный профиль пользователя."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    is_admin = models.BooleanField('Является администратором', default=False)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username}"


class DesignRequest(models.Model):
    """Модель заявки на дизайн-проект."""
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнена'),
        ('rejected', 'Отклонена'),
    )

    title = models.CharField('Название проекта', max_length=200)
    description = models.TextField('Описание задачи')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик')
    photo = models.ImageField('Фото помещения', upload_to='requests_photos/', blank=True, null=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} от {self.user.username}"