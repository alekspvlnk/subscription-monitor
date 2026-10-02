from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('list/', views.subscription_list, name='list'),
    path('add/', views.add_subscription, name='add'),
    path('edit/<int:sub_id>/', views.edit_subscription, name='edit'),
    path('delete/<int:sub_id>/', views.delete_subscription, name='delete'),
    path('analytics/', views.analytics, name='analytics'),
    path('profile/', views.profile, name='profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]