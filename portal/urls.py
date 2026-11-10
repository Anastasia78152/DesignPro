from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('request/create/', views.create_request, name='create_request'),
    path('request/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('superadmin/', views.admin_dashboard, name='admin_dashboard'),
    path('superadmin/request/<int:pk>/status/', views.update_request_status, name='change_status'),
]