from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import DesignRequest, Category, UserProfile
from .forms import RegistrationForm, LoginForm, DesignRequestForm, StatusUpdateForm

def index(request):
    """Главная страница сайта. Показывает список категорий."""
    categories = Category.objects.all()
    return render(request, 'portal/index.html', {'categories': categories})

def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Вы успешно зарегистрировались! Теперь можете войти.')
            return redirect('user_login')
    else:
        form = RegistrationForm()
        
    return render(request, 'portal/register.html', {'form': form})

def user_login(request):
    """Вход пользователя в систему."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                
                if hasattr(user, 'profile') and user.profile.is_admin:
                    return redirect('admin_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
        
    return render(request, 'portal/login.html', {'form': form})

@login_required
def user_logout(request):
    """Выход пользователя из системы."""
    logout(request) 
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index') 

@login_required 
def user_dashboard(request):
    """Личный кабинет: показывает только заявки текущего пользователя."""
    user_requests = DesignRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'portal/user_dashboard.html', {'requests': user_requests})

@login_required
def create_request(request):
    """Создание новой заявки на дизайн."""
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.save()
            
            messages.success(request, 'Ваша заявка успешно создана!')
            return redirect('user_dashboard')
    else:
        form = DesignRequestForm()
        
    return render(request, 'portal/create_request.html', {'form': form})

@login_required
def delete_request(request, pk):
    """Удаление заявки (только если она принадлежит пользователю)."""
    req = get_object_or_404(DesignRequest, pk=pk, user=request.user)
    
    if request.method == 'POST':
        req.delete() 
        messages.success(request, 'Заявка удалена.')
        return redirect('user_dashboard')
        
    return render(request, 'portal/delete_request.html', {'request_obj': req})

def check_is_admin(user):
    """Вспомогательная функция: проверка, является ли пользователь админом."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_admin

@login_required
def admin_dashboard(request):
    """Панель администратора: список всех заявок."""
    if not check_is_admin(request.user):
        messages.error(request, 'У вас нет прав администратора.')
        return redirect('index')
        
    all_requests = DesignRequest.objects.all().order_by('-created_at')
    
    return render(request, 'portal/admin_dashboard.html', {'requests': all_requests})

@login_required
def update_request_status(request, pk):
    """Админ меняет статус заявки."""
    if not check_is_admin(request.user):
        return redirect('index')
        
    req = get_object_or_404(DesignRequest, pk=pk)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=req)
        if form.is_valid():
            form.save() 
            messages.success(request, f'Статус заявки #{req.id} изменён.')
            return redirect('admin_dashboard')
    else:
        form = StatusUpdateForm(instance=req)
        
    return render(request, 'portal/update_status.html', {'form': form, 'request_obj': req})