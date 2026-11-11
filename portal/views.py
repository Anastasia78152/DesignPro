from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import DesignRequest, Category, UserProfile
from .forms import (
    RegistrationForm, LoginForm, DesignRequestForm,
    StatusUpdateForm, CategoryForm
)

def index(request):
    """Главная страница."""
    total_requests = DesignRequest.objects.count()
    completed_requests = DesignRequest.objects.filter(status='done').count()
    total_clients = User.objects.filter(profile__is_admin=False).count()
    in_progress_count = DesignRequest.objects.filter(status='in_progress').count()
    done_requests = DesignRequest.objects.filter(status='done').order_by('-created_at')[:4]
    
    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'total_clients': total_clients,
        'in_progress_count': in_progress_count,
        'done_requests': done_requests,
    }
    return render(request, 'portal/index.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('user_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'portal/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                if user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin):
                    return redirect('admin_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(request, 'portal/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')

@login_required
def user_dashboard(request):
    user_requests = DesignRequest.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status')
    if status_filter in ['new', 'in_progress', 'done']:
        user_requests = user_requests.filter(status=status_filter)
    
    user_requests = user_requests.order_by('-created_at')
    
    context = {
        'requests': user_requests,
        'current_status': status_filter or '',
        'statuses': DesignRequest.STATUS_CHOICES,
    }
    return render(request, 'portal/user_dashboard.html', context)

@login_required
def create_request(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.status = 'new'
            new_request.save()
            messages.success(request, 'Ваша заявка успешно создана!')
            return redirect('user_dashboard')
    else:
        form = DesignRequestForm()
    return render(request, 'portal/create_request.html', {'form': form})

@login_required
def delete_request(request, pk):
    req = get_object_or_404(DesignRequest, pk=pk, user=request.user)
    
    if req.status in ['in_progress', 'done']:
        messages.error(request, f'Нельзя удалить заявку со статусом "{req.get_status_display()}".')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('user_dashboard')
    return render(request, 'portal/delete_request.html', {'request_obj': req})

def check_is_admin(user):
    return user.is_authenticated and (user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin))

@login_required
def admin_dashboard(request):
    if not check_is_admin(request.user):
        messages.error(request, 'У вас нет прав администратора.')
        return redirect('index')
    
    all_requests = DesignRequest.objects.all().order_by('-created_at')
    return render(request, 'portal/admin_dashboard.html', {'requests': all_requests})

@login_required
def update_request_status(request, pk):
    if not check_is_admin(request.user):
        return redirect('index')
    
    req = get_object_or_404(DesignRequest, pk=pk)
    if req.status != 'new':
        messages.error(request, f'Смена статуса невозможна. Текущий статус: "{req.get_status_display()}".')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, request.FILES, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, f'Статус заявки #{req.id} изменён на "{req.get_status_display()}".')
            return redirect('admin_dashboard')
    else:
        form = StatusUpdateForm(instance=req)
    return render(request, 'portal/update_status.html', {'form': form, 'request_obj': req})

@login_required
def admin_categories(request):
    """Управление категориями"""
    if not check_is_admin(request.user):
        return redirect('index')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{form.instance.name}" добавлена.')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'portal/admin_categories.html', {
        'categories': categories,
        'form': form,
    })

@login_required
def delete_category(request, pk):
    if not check_is_admin(request.user):
        return redirect('index')
    
    category = get_object_or_404(Category, pk=pk)
 
    if request.method == 'POST':
        category_name = category.name
        category.delete()  
        messages.success(request, f'Категория "{category_name}" и все её заявки удалены.')
        return redirect('admin_categories')
    return render(request, 'portal/delete_category.html', {'category': category})