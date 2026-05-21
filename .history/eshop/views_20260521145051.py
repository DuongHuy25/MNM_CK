from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import uuid
import math
import string
import random
from dashboard.models import Product, Category, Brand, Order, OrderItem, PaymentMethod, Store, About, News, Review, ReviewImage, OrderReview, Wishlist
from users.models import User
from .cart import Cart
from .forms import CheckoutForm, OrderTrackingForm, LoginForm, RegisterForm, EshopPasswordResetForm, EshopSetPasswordForm, ProfileEditForm, ProductReviewForm, OrderReviewForm, ForgotPasswordForm
from .error_views import error_view


# ==================== STOREFRONT ====================

# ==================== SHIPPING CALCULATION ====================

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points using Haversine formula (in km)"""
    if not all([lat1, lng1, lat2, lng2]):
        return None
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in km
    R = 6371
    distance = R * c
    
    return round(distance, 2)

def calculate_shipping_fee(distance):
    """Calculate shipping fee based on distance"""
    if distance is None:
        return 0
    
    # Shipping fee structure
    if distance <= 2:
        return 15000  # 15k for <= 2km
    elif distance <= 5:
        return 25000  # 25k for 2-5km
    elif distance <= 10:
        return 35000  # 35k for 5-10km
    else:
        # 5k for each additional km beyond 10km
        return 35000 + (distance - 10) * 5000

def find_nearest_store(user_lat, user_lng):
    """Find the nearest store to user location"""
    if not user_lat or not user_lng:
        return None
    
    stores = Store.objects.all()
    nearest_store = None
    min_distance = float('inf')
    
    for store in stores:
        # Store model uses latitude/longitude fields (not lat/lng)
        if getattr(store, 'latitude', None) is not None and getattr(store, 'longitude', None) is not None:
            distance = calculate_distance(user_lat, user_lng, store.latitude, store.longitude)
            if distance is not None and distance < min_distance:
                min_distance = distance
                nearest_store = store
    
    return nearest_store, min_distance

def get_delivery_time_slots():
    """Get available delivery time slots"""
    from datetime import datetime, timedelta
    import json
    
    today = datetime.now()
    slots = []
    
    # Generate slots for next 3 days
    for day_offset in range(3):
        current_date = today + timedelta(days=day_offset)
        
        if day_offset == 0:  # Today
            # Only show slots after current time + 1 hour
            current_hour = current_date.hour
            start_hour = max(current_hour + 1, 9)  # Start at 9 AM or current hour + 1
            end_hour = 21  # Until 9 PM
        elif day_offset == 1:  # Tomorrow
            start_hour = 9
            end_hour = 21
        else:  # Day after tomorrow
            start_hour = 9
            end_hour = 18  # Until 6 PM
        
        for hour in range(start_hour, end_hour):
            slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            # Use minutes without invalid %00 format token
            slot_label = f"{slot_time.strftime('%d/%m %H:%M')}"

            slot_value = slot_time.strftime('%Y-%m-%d %H:%M')
            
            slots.append({
                'label': slot_label,
                'value': slot_value,
                'date': slot_time.strftime('%d/%m'),
                'time': slot_time.strftime('%H:%M'),
            })
    
    return slots

# ==================== VIEWS ====================

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
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
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

    reviews = (
        Review.objects.filter(order_item__product=product, status='approved')
        .select_related('user', 'order_item')
        .prefetch_related('images')
        .order_by('-created_at')
    )

    reviewable_order_item = None
    if request.user.is_authenticated:
        reviewed_ids = list(
            Review.objects.filter(user=request.user).values_list('order_item_id', flat=True)
        )
        completed_items = OrderItem.objects.filter(
            product=product,
            order__user=request.user,
            order__status='completed',
        )
        if reviewed_ids:
            completed_items = completed_items.exclude(pk__in=reviewed_ids)
        reviewable_order_item = completed_items.order_by('-order__order_date', '-id').first()

    user_can_review = reviewable_order_item is not None
    user_review = None

    if request.method == 'POST' and user_can_review:
        form = ProductReviewForm(request.POST, request.FILES)
        if form.is_valid():
            reviewed_ids = list(
                Review.objects.filter(user=request.user).values_list('order_item_id', flat=True)
            )
            completed_items = OrderItem.objects.filter(
                product=product,
                order__user=request.user,
                order__status='completed',
            )
            if reviewed_ids:
                completed_items = completed_items.exclude(pk__in=reviewed_ids)
            order_item = completed_items.order_by('-order__order_date', '-id').first()
            if order_item:
                review = Review.objects.create(
                    order_item=order_item,
                    user=request.user,
                    rating=int(form.cleaned_data['rating']),
                    content=form.cleaned_data.get('comment') or '',
                    status='pending',
                )

                images = request.FILES.getlist('images')
                for img in images[:5]:
                    ReviewImage.objects.create(review=review, image=img)

                messages.success(request, 'Bạn đã đánh giá thành công!')
                return redirect('eshop:product_detail', pk=product.pk)
    else:
        form = ProductReviewForm()
    
    return render(request, 'eshop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'form': form,
        'user_can_review': user_can_review,
        'user_review': user_review,
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

def _geocode_address(address):
    """Geocode address using Nominatim, return (lat, lng) or None."""
    import urllib.request, json
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(address)}&countrycodes=vn&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'ZenMart/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        if data and data[0]:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None


def _find_nearest_store(lat, lng):
    """Find the nearest active store to given coordinates."""
    from dashboard.utils import calculate_distance
    stores = Store.objects.filter(is_active=True)
    best, min_dist = None, float('inf')
    for s in stores:
        d = calculate_distance(lat, lng, s.latitude, s.longitude)
        if d < min_dist:
            min_dist, best = d, s
    return best, min_dist


def _update_warehouse_inventory(order, store):
    """Create export batch and reduce warehouse items for an order."""
    from dashboard.models import Warehouse, WarehouseBatch, WarehouseBatchItem, WarehouseItem, WarehouseTransaction
    try:
        warehouse = Warehouse.objects.get(store=store)
    except Warehouse.DoesNotExist:
        return

    batch_number = f"XUAT-{order.order_id}"
    batch = WarehouseBatch.objects.create(
        warehouse=warehouse,
        batch_type='export',
        batch_number=batch_number,
        supplier=order.full_name or 'Khách online',
        description=f'Xuất kho cho đơn hàng {order.order_id}',
        total_amount=order.total_amount,
    )

    for item in order.items.all():
        # Create batch item
        WarehouseBatchItem.objects.create(
            batch=batch,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        # Reduce warehouse item quantity
        try:
            wi = WarehouseItem.objects.get(warehouse=warehouse, product=item.product)
            wi.quantity = max(0, wi.quantity - item.quantity)
            wi.save()  # save() auto-calls sync_product_stock
            # Create transaction record
            WarehouseTransaction.objects.create(
                warehouse_item=wi,
                transaction_type='export',
                quantity=item.quantity,
                unit_price=item.unit_price,
                note=f'Xuất cho đơn hàng {order.order_id}',
            )
        except WarehouseItem.DoesNotExist:
            pass

    batch.calculate_total()
    batch.save()


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
                delivery_time_slot=form.cleaned_data.get('delivery_time_slot', ''),
            )
            if request.user.is_authenticated:
                order_data['user'] = request.user

            # Geocode shipping address
            geo = _geocode_address(form.cleaned_data['shipping_address'])
            if geo:
                order_data['lat'], order_data['lng'] = geo
            elif request.user.is_authenticated and request.user.lat and request.user.lng:
                # Fallback: use saved location from user profile
                order_data['lat'] = request.user.lat
                order_data['lng'] = request.user.lng

            order = Order.objects.create(**order_data)

            # Calculate shipping fee and find nearest store
            shipping_fee = 0
            nearest_store = None
            distance = None
            
            if order.lat and order.lng:
                nearest_store, distance = find_nearest_store(order.lat, order.lng)
                if nearest_store:
                    order.nearest_store = nearest_store
                
                if distance:
                    order.shipping_distance = distance
                    shipping_fee = calculate_shipping_fee(distance)
                    order.shipping_fee = shipping_fee
            
            # Update total amount with shipping fee
            order.total_amount += shipping_fee
            order.save()

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

            # Update warehouse inventory if store assigned
            if nearest_store:
                _update_warehouse_inventory(order, nearest_store)

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

    # Get delivery time slots
    delivery_slots = get_delivery_time_slots()

    return render(request, 'eshop/checkout.html', {
        'form': form,
        'cart': cart,
        'delivery_slots': delivery_slots,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    nearest_store = None
    distance_km = None
    est_minutes = None
    if order.store:
        nearest_store = order.store
        if order.lat and order.lng:
            from dashboard.utils import calculate_distance
            distance_km = calculate_distance(order.lat, order.lng, nearest_store.latitude, nearest_store.longitude)
    elif order.lat and order.lng:
        nearest_store, distance_km = _find_nearest_store(order.lat, order.lng)
    if distance_km:
        # Estimate: ~30km/h average delivery speed in city
        est_minutes = int(distance_km / 30 * 60) + 10  # +10 min prep time
        if est_minutes < 15:
            est_minutes = 15
    stores = Store.objects.filter(is_active=True)
    return render(request, 'eshop/order_success.html', {
        'order': order,
        'nearest_store': nearest_store,
        'distance_km': distance_km,
        'est_minutes': est_minutes,
        'stores': stores,
    })


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
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

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



def forgot_password_view(request):
    """Quên mật khẩu eshop - gửi mật khẩu mới về email"""
    if request.user.is_authenticated:
        return redirect('eshop:home')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)

                new_password = generate_random_password()
                user.set_password(new_password)
                user.save()

                subject = 'Mật khẩu mới ZenMart'
                message = f"""
Xin chào {user.get_full_name() or user.email},

Bạn vừa yêu cầu đặt lại mật khẩu cho tài khoản ZenMart.

Mật khẩu mới của bạn là:

{new_password}

Vui lòng đăng nhập lại và đổi mật khẩu sau khi vào hệ thống.

Trân trọng,
ZenMart
"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Mật khẩu mới đã được gửi về email của bạn.')
                return redirect('eshop:login')

            except User.DoesNotExist:
                messages.error(request, 'Email này không tồn tại trong hệ thống.')
            except Exception as e:
                messages.error(request, f'Không gửi được email: {str(e)}')
        else:
            messages.error(request, 'Vui lòng nhập email hợp lệ.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'eshop/auth/forgot_password.html', {
        'form': form,
    })

@login_required
def profile_view(request):
    # Pagination for orders
    orders_qs = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders_qs, 10)  # 10 orders per page
    page = request.GET.get('page')
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    # Handle profile edit
    if request.method == 'POST' and 'profile_edit' in request.POST:
        form = ProfileEditForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['full_name']
            parts = name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.phone = form.cleaned_data.get('phone', '')
            user.address = form.cleaned_data.get('address', '')
            user.lat = form.cleaned_data.get('lat') or None
            user.lng = form.cleaned_data.get('lng') or None
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
            'lat': request.user.lat,
            'lng': request.user.lng,
        })

    # Handle password change
    if request.method == 'POST' and 'password_change' in request.POST:
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu hiện tại không chính xác!')
        elif new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới không khớp!')
        elif len(new_password) < 8:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 8 ký tự!')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Đổi mật khẩu thành công! Vui lòng đăng nhập lại.')
            return redirect('eshop:login')

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
    stores = Store.objects.all()
    # Only pass stores with valid coordinates to the JS frontend
    stores = stores.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    stores = stores.filter(latitude__gt=-90, latitude__lt=90, longitude__gt=-180, longitude__lt=180)

    store_id = request.GET.get('store_id')
    target_store = None
    if store_id:
        target_store = Store.objects.filter(pk=store_id).exclude(latitude__isnull=True).exclude(longitude__isnull=True).first()

    # Fallback origin: use saved user location (profile)
    user_lat = None
    user_lng = None
    user_address = None
    if request.user.is_authenticated:
        if getattr(request.user, 'lat', None) is not None and getattr(request.user, 'lng', None) is not None:
            user_lat = request.user.lat
            user_lng = request.user.lng
        user_address = getattr(request.user, 'address', None) or None

    return render(request, 'eshop/directions.html', {
        'stores': stores,
        'target_store': target_store,
        'user_lat': user_lat,
        'user_lng': user_lng,
        'user_address': user_address,
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


# ==================== ABOUT ====================

def about(request):
    articles = About.objects.filter(status='published', is_active=True).order_by('order', '-created_at')
    stores = Store.objects.filter(is_active=True)
    return render(request, 'eshop/about.html', {'articles': articles, 'stores': stores})


# ==================== NEWS ====================

def news_list(request):
    news = News.objects.filter(status='published').order_by('-published_at', '-created_at')
    category = request.GET.get('category')
    if category:
        news = news.filter(category=category)
    featured = news.filter(is_featured=True)[:3]
    return render(request, 'eshop/news.html', {
        'news': news,
        'featured': featured,
        'current_category': category,
    })


def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, status='published')
    article.increment_views()
    related = News.objects.filter(status='published', category=article.category).exclude(pk=article.pk)[:3]
    return render(request, 'eshop/news_detail.html', {
        'article': article,
        'related': related,
    })


# ==================== CONTACT ====================

def contact(request):
    from dashboard.models import ContactSettings
    cs = ContactSettings.objects.first()
    if not cs:
        cs = ContactSettings.objects.create()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, subject, message]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
        else:
            try:
                import ssl, smtplib
                from django.core.mail import send_mail
                from django.conf import settings as django_settings

                # Patch: skip SSL cert verification for SMTP on Windows/Python 3.14
                _orig_SMTP_SSL_init = smtplib.SMTP_SSL.__init__
                def _patched_init(self, *args, **kwargs):
                    kwargs.setdefault('context', ssl._create_unverified_context())
                    _orig_SMTP_SSL_init(self, *args, **kwargs)
                smtplib.SMTP_SSL.__init__ = _patched_init

                # Use SMTP settings from ContactSettings
                django_settings.EMAIL_HOST = cs.smtp_host
                django_settings.EMAIL_PORT = cs.smtp_port
                django_settings.EMAIL_USE_TLS = cs.smtp_use_tls
                django_settings.EMAIL_HOST_USER = cs.smtp_user
                django_settings.EMAIL_HOST_PASSWORD = cs.smtp_password
                django_settings.DEFAULT_FROM_EMAIL = cs.smtp_user

                full_msg = f"Tên: {name}\nEmail: {email}\n\n{message}"
                send_mail(
                    subject=f'[{cs.site_name} Liên hệ] {subject}',
                    message=full_msg,
                    from_email=cs.smtp_user or django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=cs.get_emails(),
                    fail_silently=False,
                )
                messages.success(request, 'Gửi tin nhắn thành công! Chúng tôi sẽ phản hồi sớm nhất.')
            except Exception:
                messages.error(request, 'Không thể gửi tin nhắn lúc này. Vui lòng thử lại sau.')

    return render(request, 'eshop/contact.html', {
        'stores': Store.objects.filter(is_active=True),
        'cs': cs,
    })


# ==================== ORDER REVIEW ====================

@login_required
def order_review(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Check if order is completed and not already reviewed
    if order.status != 'completed':
        messages.error(request, 'Chỉ có thể đánh giá đơn hàng đã được giao thành công.')
        return redirect('eshop:order_tracking')
    
    existing_review = OrderReview.objects.filter(order=order).first()
    if existing_review:
        messages.info(request, 'Bạn đã đánh giá đơn hàng này rồi.')
        return redirect('eshop:order_tracking')
    
    if request.method == 'POST':
        form = OrderReviewForm(request.POST)
        if form.is_valid():
            review = OrderReview.objects.create(
                order=order,
                user=request.user,
                food_quality=form.cleaned_data['food_quality'],
                service_quality=form.cleaned_data['service_quality'],
                delivery_speed=form.cleaned_data['delivery_speed'],
                packaging_quality=form.cleaned_data['packaging_quality'],
                overall_rating=form.cleaned_data['overall_rating'],
                content=form.cleaned_data['comment'],
                status='pending'  # Default status
            )
            messages.success(request, 'Bạn đã đánh giá thành công!')
            return redirect('eshop:home')
    else:
        form = OrderReviewForm()
    
    return render(request, 'eshop/order_review.html', {
        'order': order,
        'form': form,
    })


# ==================== WISHLIST ====================

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category', 'product__brand')
    return render(request, 'eshop/wishlist.html', {
        'wishlist_items': wishlist_items,
    })


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if already in wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.info(request, f'{product.name} đã có trong danh sách yêu thích!')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f'Đã thêm {product.name} vào danh sách yêu thích!')
    
    # Redirect back or to wishlist
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER'))
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('eshop:wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product=product)
    wishlist_item.delete()
    messages.success(request, f'Đã xóa {product.name} khỏi danh sách yêu thích!')
    
    # Redirect back or to wishlist
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER'))
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('eshop:wishlist')


# ==================== ORDER DETAIL ====================

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Handle order cancellation
    if request.method == 'POST' and order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Đơn hàng {order.order_id} đã được hủy thành công!')
        return redirect('eshop:order_detail', order_id=order.order_id)
    
    return render(request, 'eshop/order_detail.html', {
        'order': order,
    })

