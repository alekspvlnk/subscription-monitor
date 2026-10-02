from django.contrib import admin
from django.urls import path, include # Додали include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Вказуємо системі шукати інші посилання у файлі subscriptions/urls.py
    path('', include('subscriptions.urls')), 
]