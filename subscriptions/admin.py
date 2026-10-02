from django.contrib import admin
from .models import Category, ExchangeRate, Subscription

# Реєструємо моделі, щоб вони з'явилися у вебінтерфейсі адміністратора
admin.site.register(Category)
admin.site.register(ExchangeRate)
admin.site.register(Subscription)