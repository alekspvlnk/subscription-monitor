from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        
    def __str__(self):
        return self.name
class ExchangeRate(models.Model):
    currency_code = models.CharField(max_length=3, verbose_name="Код валюти")
    rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Курс до гривні")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    def __str__(self):
        return f"{self.currency_code} - {self.rate}"
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категорія")
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Курс конвертації")
    service_name = models.CharField(max_length=255, verbose_name="Назва сервісу")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Вартість")
    currency = models.CharField(max_length=3, default='UAH', verbose_name="Валюта")
    price_uah = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Вартість у грн")
    next_payment = models.DateField(verbose_name="Дата наступного платежу")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    def __str__(self):
        return f"{self.service_name} ({self.user.username})"
    @property
    def days_left(self):
        """Алгоритм розрахунку Δt = Date_payment - Date_current"""
        from datetime import date
        if self.next_payment:
            return (self.next_payment - date.today()).days
        return 0
    @property
    def payment_status(self):
        """Визначає статус небезпеки списання коштів на основі Δt"""
        dt = self.days_left
        if dt < 0:
            return 'overdue'  # Прострочено
        elif dt == 1:
            return 'critical'  # Критично (1 день до платежу)
        elif dt <= 3:
            return 'warning'  # Попередження (3 або 2 дні до платежу)
        return 'normal'  # Все спокійно
    