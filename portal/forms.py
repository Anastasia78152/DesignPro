from django import forms
from django.contrib.auth.models import User
from .models import DesignRequest, Category
import re

class RegistrationForm(forms.Form):
    """Регистрация пользователя с полной валидацией."""
    
    fio = forms.CharField(
        label='ФИО',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    password_confirm = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    agreement = forms.BooleanField(
        label='Я согласен на обработку персональных данных',
        required=True
    )

    def clean_fio(self):
        """ФИО: только кириллица, дефис и пробелы."""
        fio = self.cleaned_data.get('fio', '')
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', fio):
            raise forms.ValidationError(
                'ФИО должно содержать только кириллические буквы, дефис и пробелы.'
            )
        if len(fio.strip()) < 2:
            raise forms.ValidationError('ФИО слишком короткое.')
        return fio

    def clean_username(self):
        """Логин: только латиница и дефис, уникальный."""
        username = self.cleaned_data.get('username', '')
        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise forms.ValidationError(
                'Логин должен содержать только латинские буквы и дефис.'
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        """Email: валидный формат."""
        email = self.cleaned_data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError('Введите корректный email-адрес.')
        return email

    def clean(self):
        """Проверка совпадения паролей и согласия."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        agreement = cleaned_data.get('agreement')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')

        if not agreement:
            self.add_error('agreement', 'Необходимо дать согласие на обработку персональных данных.')

        return cleaned_data

    def save(self):
        """Создаёт пользователя и профиль."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        from .models import UserProfile
        UserProfile.objects.create(
            user=user,
            fio=self.cleaned_data['fio']
        )
        return user

class LoginForm(forms.Form):
    """Форма входа в систему."""
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class DesignRequestForm(forms.ModelForm):
    """Форма создания заявки с валидацией файла."""
    
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_photo(self):
        """Проверка файла: формат и размер (макс 2 Мб)."""
        photo = self.cleaned_data.get('photo')
        if not photo:
            raise forms.ValidationError('Необходимо загрузить фото помещения или план.')
        allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
        ext = photo.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                f'Допустимые форматы: {", ".join(allowed_extensions)}. Вы загрузили: {ext}'
            )

        max_size = 2 * 1024 * 1024
        if photo.size > max_size:
            raise forms.ValidationError(
                f'Размер файла не должен превышать 2 Мб. Текущий размер: {photo.size / 1024 / 1024:.2f} Мб'
            )
        
        return photo

class StatusUpdateForm(forms.ModelForm):
    """Форма смены статуса заявки администратором."""
    
    class Meta:
        model = DesignRequest
        fields = ['status', 'design_image', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'design_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'admin_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        """Проверка обязательных полей в зависимости от статуса."""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        design_image = cleaned_data.get('design_image')
        admin_comment = cleaned_data.get('admin_comment')
        if status == 'done' and not design_image:
            self.add_error('design_image', 'При статусе "Выполнено" необходимо прикрепить изображение готового дизайна.')
        if status == 'in_progress' and not admin_comment:
            self.add_error('admin_comment', 'При статусе "Принято в работу" необходимо указать комментарий.')

        return cleaned_data

class CategoryForm(forms.ModelForm):
    """Форма добавления категории."""
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }