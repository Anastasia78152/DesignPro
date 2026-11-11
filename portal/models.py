from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Категории заявок """
    name = models.CharField('Название категории', max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Расширенный профиль пользователя."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fio = models.CharField('ФИО', max_length=255, default='')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    is_admin = models.BooleanField('Является администратором', default=False)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username} ({self.fio})"


class DesignRequest(models.Model):
    """Модель заявки на дизайн-проект."""
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('done', 'Выполнено'),
    )

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик')
    photo = models.ImageField('Фото помещения или план', upload_to='requests_photos/')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    design_image = models.ImageField('Изображение готового дизайна', upload_to='design_images/', blank=True, null=True)
    admin_comment = models.TextField('Комментарий администратора', blank=True, null=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} от {self.user.username}"