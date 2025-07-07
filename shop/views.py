from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.translation import gettext_lazy as _ 
from .models import Category, Product, Favorite, CartItem, OrderItem, Order, Review
from .forms import RegisterForm, LoginForm, OrderForm, ReviewForm
import random
import requests

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_ip_info(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()

        location = data.get("loc", ",").split(",")
        lat = location[0] if len(location) > 1 else None
        lon = location[1] if len(location) > 1 else None

        return {
            "country": data.get("country", "Неизвестно"),
            "region": data.get("region", "Неизвестно"),
            "city": data.get("city", "Неизвестно"),
            "isp": data.get("org", "Неизвестно"),
            "org": data.get("org", "Неизвестно"),
            "hostname": data.get("hostname", "Неизвестно"),
            "asn": data.get("asn", "Неизвестно"),
            "lat": lat,
            "lon": lon,
        }
    except:
        return {
            "country": "Неизвестно",
            "region": "Неизвестно",
            "city": "Неизвестно",
            "isp": "Неизвестно",
            "org": "Неизвестно",
            "hostname": "Неизвестно",
            "asn": "Неизвестно",
            "lat": None,
            "lon": None,
        }


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def contact_view(request):
    return render(request, 'shop/contact.html')

def about_view(request):
    return render(request, 'shop/about_us.html')

def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    categories = Category.objects.all()
    
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    active_category = int(category_id) if category_id and category_id.isdigit() else None
    if active_category:
        products = products.filter(category_id=active_category)

    if price_min:
        try:
            price_min = float(price_min)
            products = products.filter(price__gte=price_min)
        except ValueError:
            pass

    if price_max:
        try:
            price_max = float(price_max)
            products = products.filter(price__lte=price_max)
        except ValueError:
            pass


    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'query': query,
        'price_min': request.GET.get('price_min', ''),
        'price_max': request.GET.get('price_max', ''),
    })




def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'shop/category.html', {'category': category, 'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, product=product).exists()
    reviews = product.reviews.all().order_by('-created_at')

    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=pk)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'form': form,
    })


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
    return redirect('product_detail', pk=pk)


@login_required
def add_to_favorites(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', pk=pk)

@login_required
def remove_from_favorites(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect('product_detail', pk=pk)

@login_required
def favorites_view(request):
    favorites = Product.objects.filter(favorite__user=request.user)
    return render(request, 'shop/favorites.html', {'favorites': favorites})

@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return redirect('product_detail', pk=pk)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, _('Неправильное имя пользователя или пароль'))
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    CartItem.objects.filter(user=request.user, product=product).delete()
    return redirect('cart')


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = form.cleaned_data
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            request.session['order_data'] = order_data
            request.session['confirm_code'] = code

            total = sum(item.product.price * item.quantity for item in cart_items)

            ip_address = get_client_ip(request)
            ip_info = get_ip_info(ip_address)
            user_agent = request.META.get("HTTP_USER_AGENT", "Неизвестно")

            location_url = f"https://maps.google.com/?q={ip_info['lat']},{ip_info['lon']}"

            admin_message = (
                f'🛒 Новый заказ от {order_data["name"]} {order_data["surname"]}\n'
                f'📞 Телефон: {order_data["phone"]}\n'
                f'🏠 Адрес: {order_data["address"]}\n'
                f'💳 Способ оплаты: {order_data["payment_method"]}\n\n'
                f'🌍 Страна: {ip_info["country"]}\n'
                f'📍 Регион: {ip_info["region"]}\n'
                f'🏙 Город: {ip_info["city"]}\n'
                f'🌐 Провайдер: {ip_info["isp"]} ({ip_info["org"]})\n'
                f'🛰️ ASN: {ip_info["asn"]}\n'
                f'🔗 Hostname: {ip_info["hostname"]}\n'
                f'💻 IP: {ip_address}\n'
                f'🗺️ Карта: {location_url}\n'
                f'🖥 Устройство: {user_agent}\n\n'
                f'💰 Сумма заказа: {total}$\n\n'
                f'🛍 Товары:\n'
)


            for item in cart_items:
                admin_message += f'- {item.product.name} x {item.quantity}\n'

            send_mail(
                subject='🛒 Новый заказ',
                message=admin_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            send_mail(
                subject='Подтверждение заказа – Jewelry Shop',
                message=f'Здравствуйте, {order_data["name"]}!\n\nВы оформили заказ на Jewelry Shop.\n\nКод подтверждения:\n{code}\n\nСпасибо за покупку!\n\nС уважением,\nJewelry Shop',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return redirect('confirm_order')
    else:
        form = OrderForm()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items
    })


@login_required
def confirm_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')

    if request.method == 'POST':
        user_code = request.POST.get('code')
        session_code = request.session.get('confirm_code')
        order_data = request.session.get('order_data')

        if user_code == session_code and order_data:
            order = Order.objects.create(
                user=request.user,
                name=order_data['name'],
                surname=order_data['surname'],
                phone=order_data['phone'],
                address=order_data['address'],
                payment_method=order_data['payment_method'],
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )

            cart_items.delete()
            del request.session['confirm_code']
            del request.session['order_data']

            return render(request, 'shop/confirm_order.html', {'success': True})
        else:
            messages.error(request, 'Неверный код подтверждения.')

    return render(request, 'shop/confirm_order.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})
