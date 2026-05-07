from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
import uuid
from dashboard.models import Product, Category, Brand, Order, OrderItem, PaymentMethod, Store
from users.models import User
from .cart import Cart
from .forms import CheckoutForm, OrderTrackingForm, LoginForm, RegisterForm, EshopPasswordResetForm, EshopSetPasswordForm, ProfileEditForm
from .error_views import error_view


# ==================== STOREFRONT ====================

def home(request):
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True).select_related('category', 'brand').order_by('-created_at')[:12]
    best_sellers = Product.objects.filter(is_active=True).order_by('-stock')[:8]
    stores = Store.objects.filter(is_active=True)
    return render(request, 'eshop/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'stores': stores,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    category_slug = request.GET.get('category')
    brand_id = request.GET.get('brand')
    q = request.GET.get('q')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if q:
        products = products.filter(name__icontains=q)

    products = products.order_by('-created_at')
    return render(request, 'eshop/products.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'current_brand': brand_id,
        'query': q or '',
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'brand'), pk=pk, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, 'eshop/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ==================== CART ====================

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'eshop/cart.html', {'cart': cart})


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng!')
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    return redirect('eshop:cart')


def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.info(request, f'Đã xóa "{product.name}" khỏi giỏ hàng.')
    return redirect('eshop:cart')


def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product, quantity)
    return redirect('eshop:cart')


# ==================== CHECKOUT ====================

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Giỏ hàng trống! Vui lòng thêm sản phẩm trước khi đặt hàng.')
        return redirect('eshop:products')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order_data = dict(
                full_name=form.cleaned_data['full_name'],
                phone_number=form.cleaned_data['phone_number'],
                shipping_address=form.cleaned_data['shipping_address'],
                note=form.cleaned_data.get('note', ''),
                status='pending',
                total_amount=cart.get_total_price(),
            )
            if request.user.is_authenticated:
                order_data['user'] = request.user
            order = Order.objects.create(**order_data)

            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    unit_price=float(item['price']),
                    total_price=float(item['price']) * item['quantity'],
                )
                # Reduce product stock
                item['product'].reduce_stock(item['quantity'])

            # Create payment record
            payment_method = form.cleaned_data['payment_method']
            payment_method_name = {
                'cod': 'Thanh toán khi nhận hàng',
                'bank': 'Chuyển khoản ngân hàng',
                'momo': 'Ví MoMo',
            }.get(payment_method, 'COD')

            pm, _ = PaymentMethod.objects.get_or_create(
                name=payment_method_name,
                defaults={'is_active': True}
            )
            order.payments.create(
                payment_method=pm,
                amount=order.total_amount,
                status='pending',
            )

            cart.clear()

            # COD: go directly to success
            if payment_method == 'cod':
                messages.success(request, 'Đặt hàng thành công! Bạn sẽ thanh toán khi nhận hàng.')
                return redirect('eshop:order_success', order_id=order.order_id)
            # Bank / MoMo: go to payment simulation
            else:
                return redirect('eshop:payment_simulate', order_id=order.order_id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['full_name'] = f'{request.user.first_name} {request.user.last_name}'.strip()
            if request.user.phone:
                initial['phone_number'] = request.user.phone
            if request.user.address:
                initial['shipping_address'] = request.user.address
        form = CheckoutForm(initial=initial)

    return render(request, 'eshop/checkout.html', {
        'form': form,
        'cart': cart,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'eshop/order_success.html', {'order': order})


def order_tracking(request):
    order = None
    if request.method == 'POST':
        form = OrderTrackingForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            order = Order.objects.filter(order_id=order_id).first()
            if not order:
                messages.error(request, 'Không tìm thấy đơn hàng với mã này.')
    else:
        form = OrderTrackingForm()

    return render(request, 'eshop/order_tracking.html', {
        'form': form,
        'order': order,
    })


# ==================== AUTH ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('eshop:home')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request=request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f'Xin chào, {user.email}!')
                next_url = request.GET.get('next') or 'eshop:home'
                return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'eshop/auth/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('eshop:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            user.first_name = form.cleaned_data.get('full_name', '').split(' ', 1)[0] if form.cleaned_data.get('full_name') else ''
            user.last_name = form.cleaned_data.get('full_name', '').split(' ', 1)[1] if form.cleaned_data.get('full_name', '').count(' ') > 0 else ''
            user.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('eshop:home')
    else:
        form = RegisterForm()
    return render(request, 'eshop/auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('eshop:home')


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]

    if request.method == 'POST':
        form = ProfileEditForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['full_name']
            parts = name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.phone = form.cleaned_data.get('phone', '')
            user.address = form.cleaned_data.get('address', '')
            if form.cleaned_data.get('avatar'):
                user.avatar = form.cleaned_data['avatar']
            user.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('eshop:profile')
    else:
        form = ProfileEditForm(initial={
            'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
            'phone': request.user.phone,
            'address': request.user.address,
        })

    return render(request, 'eshop/auth/profile.html', {
        'orders': orders,
        'form': form,
    })


# ==================== ERROR TEST ====================

def error_test_view(request, status_code):
    """Preview error pages during development. Access via /error/404/ etc."""
    from django.conf import settings
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404
    return error_view(request, status_code)


# ==================== DIRECTIONS ====================

def directions(request):
    stores = Store.objects.filter(is_active=True)
    store_id = request.GET.get('store_id')
    target_store = None
    if store_id:
        target_store = Store.objects.filter(pk=store_id, is_active=True).first()
    return render(request, 'eshop/directions.html', {
        'stores': stores,
        'target_store': target_store,
    })


# ==================== PAYMENT SIMULATION ====================

def payment_simulate(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    payment = order.payments.first()

    if not payment:
        messages.error(request, 'Không tìm thấy thông tin thanh toán.')
        return redirect('eshop:home')

    # Determine payment method
    pm_name = payment.payment_method.name.lower()
    if 'momo' in pm_name:
        payment_method = 'momo'
        method_label = 'Ví MoMo'
    elif 'chuyển khoản' in pm_name or 'ngân hàng' in pm_name or 'bank' in pm_name:
        payment_method = 'bank'
        method_label = 'Chuyển Khoản Ngân Hàng'
    else:
        # Fallback: if COD somehow got here, redirect to success
        return redirect('eshop:order_success', order_id=order.order_id)

    if request.method == 'POST':
        # Simulate payment completion
        payment.status = 'completed'
        payment.reference_number = f'SIM-{order.order_id}-{payment_method.upper()}-{uuid.uuid4().hex[:8]}'
        payment.note = f'Thanh toán giả lập qua {method_label}'
        payment.save()
        messages.success(request, f'Thanh toán {method_label} thành công!')
        return redirect('eshop:order_success', order_id=order.order_id)

    return render(request, 'eshop/payment_simulate.html', {
        'order': order,
        'payment_method': payment_method,
        'method_label': method_label,
    })
