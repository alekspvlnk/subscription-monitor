import requests
from decimal import Decimal
from django.utils import timezone
from .models import ExchangeRate

MONOBANK_CURRENCY_CODES = {
    840: 'USD',
    978: 'EUR'
}


def update_exchange_rates():
    """Звертається до Monobank API та оновлює курси в базі даних"""
    url = "https://api.monobank.ua/bank/currency"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if item.get('currencyCodeB') == 980:  # Відносно UAH
                    currency_id = item.get('currencyCodeA')
                    if currency_id in MONOBANK_CURRENCY_CODES:
                        currency_code = MONOBANK_CURRENCY_CODES[currency_id]
                        rate_value = item.get('rateSell') or item.get('rateCross')
                        if rate_value:
                            ExchangeRate.objects.update_or_create(
                                currency_code=currency_code,
                                defaults={
                                    'rate': Decimal(str(rate_value)),
                                    'updated_at': timezone.now()
                                }
                            )
            return True
    except requests.RequestException:
        pass
    return False


def get_rate_for_currency(currency_code):
    """Повертає курс валюти з резервним відкатом до раніше збереженого в БД"""
    if currency_code == 'UAH':
        return Decimal('1.0000')

    update_exchange_rates()

    try:
        rate_obj = ExchangeRate.objects.get(currency_code=currency_code)
        return rate_obj.rate
    except ExchangeRate.DoesNotExist:
        default_rates = {'USD': Decimal('40.5000'), 'EUR': Decimal('43.5000')}
        return default_rates.get(currency_code, Decimal('1.0000'))