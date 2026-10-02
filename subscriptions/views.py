from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from collections import defaultdict

from .models import Subscription, Category, ExchangeRate
from .services import get_rate_for_currency


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'subscriptions/auth/register.html', {
                'error': 'Паролі не збігаються!', 'username': username, 'email': email
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'subscriptions/auth/register.html', {
                'error': 'Користувач з таким іменем вже існує!', 'email': email
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('subscriptions:login')

    return render(request, 'subscriptions/auth/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('subscriptions:dashboard')
        else:
            return render(request, 'subscriptions/auth/login.html', {
                'error': 'Неправильне ім\'я користувача або пароль!', 'username': username
            })

    return render(request, 'subscriptions/auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('subscriptions:login')


@login_required
def dashboard(request):
    active_subs = Subscription.objects.filter(user=request.user, is_active=True)
    total_cost = sum(sub.price_uah for sub in active_subs)

    category_data = Subscription.objects.filter(user=request.user, is_active=True) \
        .values('category__name') \
        .annotate(total=Sum('price_uah')) \
        .order_by('-total')

    monthly_expenses = defaultdict(float)
    for sub in active_subs:
        if sub.next_payment:
            month_str = sub.next_payment.strftime('%m.%Y')
            monthly_expenses[month_str] += float(sub.price_uah)

    sorted_months = sorted(monthly_expenses.keys())
    chart_months = [m for m in sorted_months]
    chart_values = [monthly_expenses[m] for m in sorted_months]

    context = {
        'active_subs': active_subs,
        'total_cost': total_cost,
        'category_data': category_data,
        'chart_months': chart_months,
        'chart_values': chart_values
    }
    return render(request, 'subscriptions/dashboard.html', context)


@login_required
def subscription_list(request):
    status_filter = request.GET.get('status', 'all')
    subs = Subscription.objects.filter(user=request.user)

    if status_filter == 'active':
        subs = subs.filter(is_active=True)
    elif status_filter == 'inactive':
        subs = subs.filter(is_active=False)

    context = {
        'subscriptions': subs,
        'current_status': status_filter
    }
    return render(request, 'subscriptions/list.html', context)


@login_required
def add_subscription(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        description = request.POST.get('description')
        price = Decimal(request.POST.get('price', '0'))
        currency = request.POST.get('currency', 'UAH')
        category_id = request.POST.get('category')
        next_payment = request.POST.get('next_payment')

        rate = get_rate_for_currency(currency)
        price_uah = price * rate

        category_obj = Category.objects.filter(id=category_id).first()
        exchange_rate_obj = ExchangeRate.objects.filter(currency_code=currency).first() if currency != 'UAH' else None

        Subscription.objects.create(
            user=request.user, category=category_obj, exchange_rate=exchange_rate_obj,
            service_name=service_name, description=description, price=price,
            currency=currency, price_uah=price_uah, next_payment=next_payment, is_active=True
        )
        return redirect('subscriptions:list')

    return render(request, 'subscriptions/add_edit.html', {'categories': categories})


@login_required
def edit_subscription(request, sub_id):
    sub = get_object_or_404(Subscription, id=sub_id, user=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        sub.service_name = request.POST.get('service_name')
        sub.description = request.POST.get('description')
        sub.price = Decimal(request.POST.get('price', '0'))
        sub.currency = request.POST.get('currency', 'UAH')
        sub.next_payment = request.POST.get('next_payment')

        rate = get_rate_for_currency(sub.currency)
        sub.price_uah = sub.price * rate

        category_id = request.POST.get('category')
        sub.category = Category.objects.filter(id=category_id).first()
        sub.exchange_rate = ExchangeRate.objects.filter(
            currency_code=sub.currency).first() if sub.currency != 'UAH' else None

        sub.save()
        return redirect('subscriptions:list')

    return render(request, 'subscriptions/add_edit.html', {'sub': sub, 'categories': categories})


@login_required
def delete_subscription(request, sub_id):
    sub = get_object_or_404(Subscription, id=sub_id, user=request.user)
    if request.method == 'POST':
        sub.delete()
    return redirect('subscriptions:list')


@login_required
def analytics(request):
    expensive_subs = Subscription.objects.filter(user=request.user, is_active=True).order_by('-price_uah')[:5]

    category_data = Subscription.objects.filter(user=request.user, is_active=True) \
        .values('category__name') \
        .annotate(total=Sum('price_uah')) \
        .order_by('-total')

    active_subs = Subscription.objects.filter(user=request.user, is_active=True)
    monthly_expenses = defaultdict(float)
    for sub in active_subs:
        if sub.next_payment:
            month_str = sub.next_payment.strftime('%m.%Y')
            monthly_expenses[month_str] += float(sub.price_uah)

    sorted_months = sorted(monthly_expenses.keys())
    chart_months = [m for m in sorted_months]
    chart_values = [monthly_expenses[m] for m in sorted_months]

    context = {
        'expensive_subs': expensive_subs,
        'category_data': category_data,
        'chart_months': chart_months,
        'chart_values': chart_values
    }
    return render(request, 'subscriptions/analytics.html', context)


@login_required
def profile(request):
    return render(request, 'subscriptions/profile.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Отримуємо параметри пошуку та сортування з URL-запиту
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'id')

    total_users = User.objects.count()
    total_subs = Subscription.objects.count()
    total_system_cost = Subscription.objects.filter(is_active=True).aggregate(Sum('price_uah'))['price_uah__sum'] or 0

    # Фільтрація об'єктів
    all_subscriptions = Subscription.objects.all()
    if search_query:
        all_subscriptions = all_subscriptions.filter(user__username__icontains=search_query)

    # Сортування об'єктів
    if sort_by == 'alphabet':
        all_subscriptions = all_subscriptions.order_by('service_name')
    elif sort_by == 'username':
        all_subscriptions = all_subscriptions.order_by('user__username')
    elif sort_by == 'price_desc':
        all_subscriptions = all_subscriptions.order_by('-price_uah')
    else:
        all_subscriptions = all_subscriptions.order_by('-id')

    context = {
        'total_users': total_users,
        'total_subs': total_subs,
        'total_system_cost': total_system_cost,
        'all_subs': all_subscriptions[:20],  # Обмежуємо вивід топ-20 записами для швидкодії
        'search_query': search_query,
        'current_sort': sort_by
    }
    return render(request, 'subscriptions/admin_dashboard.html', context)