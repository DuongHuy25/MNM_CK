from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.http import HttpResponse

from dashboard.models import Store, Product, Order, OrderItem, Category
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer, StoreSerializer, OrderSerializer, CategorySerializer
from .forms import (
    StoreForm, ProductForm, OrderForm, CategoryForm, SearchForm, UserForm
)
from .utils import admin_required, search_items, paginate_queryset, get_stats


# ==================== DASHBOARD ====================
@admin_required
def dashboard_index(request):
    stats = get_stats()
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    recent_products = Product.objects.all().order_by('-id')[:5]
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'page_title': 'Bảng Điều Khiển',
    }
    return render(request, 'dashboard/index.html', context)


# ==================== STORES ====================
@admin_required
def stores_list(request):
    stores = Store.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        stores = search_items(stores, q, ['name', 'address'])
    page_obj, paginator = paginate_queryset(stores, request.GET.get('page'), 15)
    return render(request, 'dashboard/stores/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Cửa Hàng',
    })

@admin_required
def stores_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, 'dashboard/stores/detail.html', {
        'store': store, 'page_title': f'Chi tiết: {store.name}',
    })

@admin_required
def stores_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cửa hàng đã được tạo thành công!')
            return redirect('dashboard:stores_list')
    else:
        form = StoreForm()
    return render(request, 'dashboard/stores/form.html', {
        'form': form, 'page_title': 'Thêm Cửa Hàng', 'is_create': True,
    })

@admin_required
def stores_edit(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cửa hàng đã được cập nhật!')
            return redirect('dashboard:stores_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'dashboard/stores/form.html', {
        'form': form, 'store': store, 'page_title': f'Chỉnh sửa: {store.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def stores_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    name = store.name
    store.delete()
    messages.success(request, f'Cửa hàng "{name}" đã được xóa!')
    return redirect('dashboard:stores_list')


# ==================== CATEGORIES ====================
@admin_required
def categories_list(request):
    categories = Category.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        categories = search_items(categories, q, ['name', 'slug'])
    page_obj, paginator = paginate_queryset(categories, request.GET.get('page'), 15)
    return render(request, 'dashboard/categories/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Danh Mục',
    })

@admin_required
def categories_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được tạo!')
            return redirect('dashboard:categories_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/categories/form.html', {
        'form': form, 'page_title': 'Thêm Danh Mục', 'is_create': True,
    })

@admin_required
def categories_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được cập nhật!')
            return redirect('dashboard:categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/categories/form.html', {
        'form': form, 'category': category,
        'page_title': f'Chỉnh sửa: {category.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def categories_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.success(request, f'Danh mục "{name}" đã được xóa!')
    return redirect('dashboard:categories_list')


# ==================== PRODUCTS ====================
@admin_required
def products_list(request):
    products = Product.objects.select_related('category').all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        products = search_items(products, q, ['name', 'description', 'category__name'])
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__id=category_filter)
    available_filter = request.GET.get('available')
    if available_filter == '1':
        products = products.filter(is_available=True)
    elif available_filter == '0':
        products = products.filter(is_available=False)
    page_obj, paginator = paginate_queryset(products, request.GET.get('page'), 6)
    categories = Category.objects.all()
    return render(request, 'dashboard/products/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'categories': categories,
        'current_category': category_filter, 'page_title': 'Quản Lý Món Ăn',
    })

@admin_required
def products_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'dashboard/products/detail.html', {
        'product': product, 'page_title': f'Chi tiết: {product.name}',
    })

@admin_required
def products_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Món ăn đã được thêm thành công!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/products/form.html', {
        'form': form, 'page_title': 'Thêm Món Ăn', 'is_create': True,
    })

@admin_required
def products_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Món ăn đã được cập nhật!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/products/form.html', {
        'form': form, 'product': product,
        'page_title': f'Chỉnh sửa: {product.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def products_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.success(request, f'Món ăn "{name}" đã được xóa!')
    return redirect('dashboard:products_list')


# ==================== ORDERS ====================
@admin_required
def orders_list(request):
    orders = Order.objects.select_related('user').all().order_by('-created_at')
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        orders = search_items(orders, q, ['full_name', 'phone', 'address', 'user__username'])
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    page_obj, paginator = paginate_queryset(orders, request.GET.get('page'), 6)
    status_choices = Order.STATUS_CHOICES
    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'status_choices': status_choices,
        'current_status': status_filter, 'page_title': 'Quản Lý Đơn Hàng',
    })

@admin_required
def orders_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đơn hàng đã được tạo thành công!')
            return redirect('dashboard:orders_list')
    else:
        form = OrderForm()
    return render(request, 'dashboard/orders/form.html', {
        'form': form, 'page_title': 'Thêm Đơn Hàng', 'is_create': True,
    })

@admin_required
def orders_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product').all()
    return render(request, 'dashboard/orders/detail.html', {
        'order': order, 'items': items, 'page_title': f'Đơn Hàng #{order.id}',
    })

@admin_required
def orders_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đơn hàng đã được cập nhật!')
            return redirect('dashboard:orders_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'dashboard/orders/form.html', {
        'form': form, 'order': order,
        'page_title': f'Chỉnh sửa Đơn #{order.id}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def orders_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, f'Đơn hàng #{pk} đã được xóa!')
    return redirect('dashboard:orders_list')


# ==================== USERS ====================
@admin_required
def users_list(request):
    users = User.objects.all()
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        q = search_form.cleaned_data['q']
        users = search_items(users, q, ['username', 'email', 'first_name', 'last_name'])
    page_obj, paginator = paginate_queryset(users, request.GET.get('page'), 6)
    return render(request, 'dashboard/users/list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'search_form': search_form, 'page_title': 'Quản Lý Người Dùng',
    })

@admin_required
def users_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'Người dùng "{user.username}" đã được tạo thành công!')
            return redirect('dashboard:users_detail', pk=user.pk)
    else:
        form = UserForm()
    return render(request, 'dashboard/users/form.html', {
        'form': form, 'is_create': True,
        'page_title': 'Thêm Người Dùng',
    })

@admin_required
def users_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    return render(request, 'dashboard/users/detail.html', {
        'user_obj': user, 'orders': orders,
        'page_title': f'Chi tiết: {user.get_full_name() or user.username}',
    })

@admin_required
def users_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            u = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                u.set_password(password)
            u.save()
            messages.success(request, 'Người dùng đã được cập nhật!')
            return redirect('dashboard:users_detail', pk=user.pk)
    else:
        form = UserForm(instance=user)
    return render(request, 'dashboard/users/form.html', {
        'form': form, 'user_obj': user, 'is_create': False,
        'page_title': f'Chỉnh sửa: {user.get_full_name() or user.username}',
    })

@admin_required
@require_http_methods(["POST"])
def users_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f'Người dùng "{username}" đã được xóa!')
    return redirect('dashboard:users_list')


# ==================== WAREHOUSE ====================
@admin_required
def warehouse_list(request):
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    try:
        from dashboard.models import Warehouse, WarehouseItem, WarehouseTransaction, WarehouseBatch
        from django.core.paginator import Paginator
        from django.db import models
        
        # Lấy tất cả batches và transactions, gộp lại theo thời gian
        combined_list = []
        
        # Thêm transactions (cũ)
        all_transactions = WarehouseTransaction.objects.select_related(
            'warehouse_item__product', 'warehouse_item__warehouse__store'
        ).order_by('-created_at')
        
        for trans in all_transactions:
            combined_list.append({
                'id': trans.id,
                'type': 'transaction',
                'date': trans.created_at,
                'product': trans.warehouse_item.product.name,
                'quantity': trans.quantity,
                'unit_price': trans.unit_price,
                'batch_type': 'Xuất kho' if trans.transaction_type == 'export' else 'Nhập kho',
                'supplier': trans.supplier or 'N/A',
                'store': trans.warehouse_item.warehouse.store.name,
                'note': trans.note or '',
                'obj': trans
            })
        
        # Thêm batches (mới)
        all_batches = WarehouseBatch.objects.select_related(
            'warehouse__store', 'created_by'
        ).order_by('-created_at')
        
        for batch in all_batches:
            try:
                items_count = batch.items.count()
                total_qty = sum([item.quantity for item in batch.items.all()])
            except:
                items_count = 0
                total_qty = 0
                
            combined_list.append({
                'id': batch.id,
                'type': 'batch',
                'date': batch.created_at,
                'product': f'{items_count} sản phẩm',
                'quantity': total_qty,
                'unit_price': 0,
                'batch_type': 'Xuất kho' if batch.batch_type == 'export' else 'Nhập kho',
                'supplier': batch.supplier or 'N/A',
                'store': batch.warehouse.store.name,
                'note': batch.description or '',
                'obj': batch
            })
        
        # Sắp xếp theo thời gian
        combined_list.sort(key=lambda x: x['date'], reverse=True)
        
        # Phân trang bằng Paginator
        trans_page = request.GET.get('trans_page', 1)
        paginator = Paginator(combined_list, 6)
        try:
            transaction_page_obj = paginator.page(trans_page)
        except:
            transaction_page_obj = paginator.page(1)
        
        # Lấy sản phẩm với tồn kho thấp
        low_stock_items = WarehouseItem.objects.filter(
            quantity__lte=models.F('min_quantity')
        ).select_related('product', 'warehouse__store')
        
        # Lấy tất cả sản phẩm trong kho (có phân trang)
        warehouse_items = WarehouseItem.objects.select_related('product', 'warehouse__store').all()
        page_num = request.GET.get('page', 1)
        paginator_items = Paginator(warehouse_items, 6)
        try:
            page_obj = paginator_items.page(page_num)
        except:
            page_obj = paginator_items.page(1)
        
        return render(request, 'dashboard/warehouse/list.html', {
            'transaction_page_obj': transaction_page_obj,
            'transaction_paginator': paginator,
            'low_stock_items': low_stock_items,
            'page_obj': page_obj,
            'paginator': paginator_items,
            'page_title': 'Quản Lý Kho',
        })
    except Exception as e:
        logger.error(f'Error in warehouse_list: {str(e)}')
        logger.error(traceback.format_exc())
        raise

@admin_required
def warehouse_detail(request, pk):
    from dashboard.models import Warehouse
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'dashboard/warehouse/detail.html', {
        'warehouse': warehouse, 'page_title': f'Kho - {warehouse.store.name}',
    })

@admin_required
def warehouse_create(request):
    from dashboard.models import Warehouse
    from dashboard.forms import WarehouseForm
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quản lý kho đã được thêm!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Thêm Quản Lý Kho', 'is_create': True,
    })

@admin_required
def warehouse_edit(request, pk):
    from dashboard.models import Warehouse
    from dashboard.forms import WarehouseForm
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quản lý kho đã được cập nhật!')
            return redirect('dashboard:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'warehouse': warehouse,
        'page_title': f'Chỉnh Sửa Kho - {warehouse.store.name}', 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def warehouse_delete(request, pk):
    from dashboard.models import Warehouse
    warehouse = get_object_or_404(Warehouse, pk=pk)
    warehouse.delete()
    messages.success(request, 'Quản lý kho đã được xóa!')
    return redirect('dashboard:warehouse_list')


# ==================== WAREHOUSE ITEM ====================
@admin_required
def warehouse_item_create(request):
    from dashboard.models import WarehouseItem
    from dashboard.forms import WarehouseItemForm
    if request.method == 'POST':
        form = WarehouseItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được thêm vào kho!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseItemForm()
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Thêm Sản Phẩm Vào Kho', 'is_item': True, 'is_create': True,
    })

@admin_required
def warehouse_item_edit(request, pk):
    from dashboard.models import WarehouseItem
    from dashboard.forms import WarehouseItemForm
    item = get_object_or_404(WarehouseItem, pk=pk)
    if request.method == 'POST':
        form = WarehouseItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật!')
            return redirect('dashboard:warehouse_list')
    else:
        form = WarehouseItemForm(instance=item)
    return render(request, 'dashboard/warehouse/form.html', {
        'form': form, 'page_title': 'Chỉnh Sửa Sản Phẩm', 'is_item': True, 'is_edit': True,
    })

@admin_required
@require_http_methods(["POST"])
def warehouse_item_delete(request, pk):
    from dashboard.models import WarehouseItem
    item = get_object_or_404(WarehouseItem, pk=pk)
    item.delete()
    messages.success(request, 'Sản phẩm đã được xóa khỏi kho!')
    return redirect('dashboard:warehouse_list')


# ==================== WAREHOUSE TRANSACTION ====================
@admin_required
def warehouse_transaction_create(request):
    """Chuyển hướng sang batch create (cho phép nhập nhiều sản phẩm cùng lúc)"""
    return redirect('dashboard:warehouse_batch_create')

@admin_required
@require_http_methods(["POST"])
def warehouse_transaction_delete(request, pk):
    from dashboard.models import WarehouseTransaction
    transaction = get_object_or_404(WarehouseTransaction, pk=pk)
    item = transaction.warehouse_item
    
    # Hoàn tác số lượng
    if transaction.transaction_type == 'import':
        item.quantity -= transaction.quantity
    else:
        item.quantity += transaction.quantity
    item.save()
    
    transaction.delete()
    messages.success(request, 'Giao dịch đã được xóa!')
    return redirect('dashboard:warehouse_list')


# ==================== MANAGE STORES LEGACY ====================
@admin_required
def manage_stores_view(request):
    return render(request, 'dashboard/manage_stores.html')


# ==================== WAREHOUSE BATCH (NEW) ====================
@admin_required
def warehouse_batch_list(request):
    from dashboard.models import WarehouseBatch
    batches = WarehouseBatch.objects.select_related('warehouse__store', 'created_by').order_by('-created_at')
    batch_type_filter = request.GET.get('batch_type')
    if batch_type_filter:
        batches = batches.filter(batch_type=batch_type_filter)
    page_obj, paginator = paginate_queryset(batches, request.GET.get('page'), 10)
    return render(request, 'dashboard/warehouse/batch_list.html', {
        'page_obj': page_obj, 'paginator': paginator,
        'page_title': 'Phiếu Nhập/Xuất Kho',
    })

@admin_required
def warehouse_batch_create(request):
    from dashboard.models import WarehouseBatch, WarehouseItem, WarehouseBatchItem
    from dashboard.forms import WarehouseBatchForm
    from dashboard.utils import generate_batch_number
    from django.utils import timezone
    import openpyxl
    import csv
    
    if request.method == 'POST':
        action = request.POST.get('action', 'create')
        form = WarehouseBatchForm(request.POST)
        
        if action == 'import-excel':
            # ===== XỬ LÝ IMPORT EXCEL =====
            if 'excel_file' not in request.FILES:
                messages.error(request, '❌ Vui lòng chọn file Excel!')
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
            
            # Tạo batch trước
            if not form.is_valid():
                messages.error(request, f'❌ Lỗi form: {form.errors}')
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
            
            batch = form.save(commit=False)
            batch.created_by = request.user
            if not batch.batch_number:
                batch.batch_number = generate_batch_number(batch.batch_type)
            batch.save()
            
            # Xử lý file Excel
            try:
                excel_file = request.FILES['excel_file']
                filename = excel_file.name.lower()
                
                # ===== XÓA ITEM CŨ (LƯU THAY THẾ) =====
                batch.items.all().delete()
                
                rows_added = 0
                errors = []
                
                if filename.endswith('.csv'):
                    # ===== XỬ LÝ CSV =====
                    import io
                    file_content = io.TextIOWrapper(excel_file.file, encoding='utf-8')
                    reader = csv.reader(file_content)
                    next(reader)  # Bỏ header
                    
                    for row_num, row in enumerate(reader, start=2):
                        if not row or not row[0].strip():
                            continue
                        try:
                            product_name = row[0].strip()
                            quantity = int(row[1]) if len(row) > 1 else 1
                            unit_price = float(row[2]) if len(row) > 2 else 0
                            
                            # Tìm sản phẩm trong kho
                            warehouse_item = WarehouseItem.objects.filter(
                                warehouse=batch.warehouse,
                                product__name__icontains=product_name
                            ).first()
                            
                            if not warehouse_item:
                                errors.append(f"❌ Hàng {row_num}: Sản phẩm '{product_name}' không tìm thấy")
                                continue
                            
                            # Tạo batch item
                            WarehouseBatchItem.objects.create(
                                batch=batch,
                                warehouse_item=warehouse_item,
                                quantity=quantity,
                                unit_price=unit_price
                            )
                            rows_added += 1
                        except (ValueError, IndexError) as e:
                            errors.append(f"❌ Hàng {row_num}: Lỗi dữ liệu - {str(e)}")
                            continue
                
                elif filename.endswith(('.xlsx', '.xls')):
                    # ===== XỬ LÝ EXCEL =====
                    try:
                        wb = openpyxl.load_workbook(excel_file)
                        ws = wb.active
                        
                        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                            if not row or not row[0]:
                                continue
                            try:
                                product_name = str(row[0]).strip()
                                quantity = int(row[1]) if row[1] else 1
                                unit_price = float(row[2]) if row[2] else 0
                                
                                # Tìm sản phẩm trong kho
                                warehouse_item = WarehouseItem.objects.filter(
                                    warehouse=batch.warehouse,
                                    product__name__icontains=product_name
                                ).first()
                                
                                if not warehouse_item:
                                    errors.append(f"❌ Hàng {row_num}: Sản phẩm '{product_name}' không tìm thấy")
                                    continue
                                
                                # Tạo batch item
                                WarehouseBatchItem.objects.create(
                                    batch=batch,
                                    warehouse_item=warehouse_item,
                                    quantity=quantity,
                                    unit_price=unit_price
                                )
                                rows_added += 1
                            except (ValueError, TypeError) as e:
                                errors.append(f"❌ Hàng {row_num}: {str(e)}")
                                continue
                    except Exception as e:
                        messages.error(request, f'❌ Lỗi đọc file Excel: {str(e)}')
                        batch.delete()
                        return render(request, 'dashboard/warehouse/batch_form.html', {
                            'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                        })
                else:
                    messages.error(request, '❌ Định dạng file không hỗ trợ. Vui lòng upload .xlsx, .xls hoặc .csv')
                    batch.delete()
                    return render(request, 'dashboard/warehouse/batch_form.html', {
                        'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                    })
                
                # ===== CẬP NHẬT NGÀY TẠO LẠI =====
                batch.created_at = timezone.now()
                batch.calculate_total()
                batch.save()
                
                # Hiển thị kết quả
                msg = f'✅ Import thành công {rows_added} sản phẩm'
                if errors:
                    msg += f' ({len(errors)} lỗi)'
                    for error in errors[:5]:  # Hiển thị 5 lỗi đầu
                        messages.warning(request, error)
                    if len(errors) > 5:
                        messages.warning(request, f'... và {len(errors)-5} lỗi khác')
                
                messages.success(request, msg)
                # Render lại form với thông báo thành công (không redirect)
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
                
            except Exception as e:
                messages.error(request, f' Lỗi: {str(e)}')
                batch.delete()
                return render(request, 'dashboard/warehouse/batch_form.html', {
                    'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
                })
        
        else:
            # ===== TẠO PHIẾU BÌNH THƯỜNG =====
            if form.is_valid():
                batch = form.save(commit=False)
                batch.created_by = request.user
                if not batch.batch_number:
                    batch.batch_number = generate_batch_number(batch.batch_type)
                batch.save()
                messages.success(request, ' Phiếu đã được tạo! Hãy thêm sản phẩm.')
                return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)
    else:
        form = WarehouseBatchForm()
    
    return render(request, 'dashboard/warehouse/batch_form.html', {
        'form': form, 'page_title': 'Tạo Phiếu Nhập/Xuất Kho', 'is_create': True,
    })

@admin_required
def warehouse_batch_add_items(request, pk):
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from dashboard.models import WarehouseBatch, WarehouseBatchItem
        from dashboard.forms import WarehouseBatchItemForm
        
        batch = get_object_or_404(WarehouseBatch, pk=pk)
        if request.method == 'POST':
            form = WarehouseBatchItemForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.batch = batch
                item.save()
                
                # Cập nhật tồn kho
                warehouse_item = item.warehouse_item
                if batch.batch_type == 'import':
                    warehouse_item.quantity += item.quantity
                else:
                    warehouse_item.quantity -= item.quantity
                warehouse_item.save()
                
                # Cập nhật tổng tiền của phiếu
                batch.calculate_total()
                batch.save()
                
                messages.success(request, 'Sản phẩm đã được thêm vào phiếu!')
                return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)
        else:
            form = WarehouseBatchItemForm()
        
        # Tính tổng tiền trước khi render
        batch.calculate_total()
        
        return render(request, 'dashboard/warehouse/batch_add_items.html', {
            'batch': batch,
            'form': form,
            'page_title': f'Thêm Sản Phẩm - Phiếu {batch.batch_number}',
        })
    except Exception as e:
        logger.error(f'Error in warehouse_batch_add_items: {str(e)}')
        logger.error(traceback.format_exc())
        raise

@admin_required
def warehouse_batch_detail(request, pk):
    from dashboard.models import WarehouseBatch
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi render
    batch.calculate_total()
    
    return render(request, 'dashboard/warehouse/batch_detail.html', {
        'batch': batch, 'page_title': f'Phiếu {batch.batch_number}',
    })

@admin_required
def warehouse_batch_print(request, pk):
    from dashboard.models import WarehouseBatch
    from dashboard.utils import export_batch_to_pdf
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi in
    batch.calculate_total()
    
    # Cập nhật trạng thái in
    from django.utils import timezone
    batch.is_printed = True
    batch.printed_at = timezone.now()
    batch.save()
    
    return export_batch_to_pdf(batch)

@admin_required  
def warehouse_batch_export_excel(request, pk):
    from dashboard.models import WarehouseBatch
    from dashboard.utils import export_batch_to_excel
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    
    # Tính tổng tiền trước khi export
    batch.calculate_total()
    
    wb = export_batch_to_excel(batch)
    if wb is None:
        messages.error(request, 'openpyxl chưa được cài đặt. Vui lòng cài đặt bằng pip install openpyxl')
        return redirect('dashboard:warehouse_batch_detail', pk=batch.pk)
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="phieu_{batch.batch_number}.xlsx"'
    wb.save(response)
    return response

@admin_required
def warehouse_batch_template_excel(request, warehouse_id):
    """Download Excel template cho import dữ liệu"""
    from dashboard.models import Warehouse
    from dashboard.utils import generate_excel_template
    
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    
    wb = generate_excel_template(warehouse)
    if wb is None:
        messages.error(request, 'Lỗi: openpyxl chưa được cài đặt hoặc lỗi tạo template')
        return redirect('dashboard:warehouse_batch_create')
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="template_import_{warehouse.store.name}.xlsx"'
    wb.save(response)
    return response

@admin_required
@require_http_methods(["POST"])
def warehouse_batch_delete(request, pk):
    from dashboard.models import WarehouseBatch
    batch = get_object_or_404(WarehouseBatch, pk=pk)
    batch.delete()
    messages.success(request, 'Phiếu đã được xóa!')
    return redirect('dashboard:warehouse_batch_list')


# ==================== WAREHOUSE BATCH ITEM MANAGEMENT ====================
@admin_required
def warehouse_batch_item_delete(request, pk):
    from dashboard.models import WarehouseBatchItem
    item = get_object_or_404(WarehouseBatchItem, pk=pk)
    batch = item.batch
    
    # Hoàn tác số lượng tồn kho
    warehouse_item = item.warehouse_item
    if batch.batch_type == 'import':
        warehouse_item.quantity -= item.quantity
    else:
        warehouse_item.quantity += item.quantity
    warehouse_item.save()
    
    item.delete()
    
    # Cập nhật tổng tiền của phiếu
    batch.calculate_total()
    batch.save()
    
    messages.success(request, 'Sản phẩm đã được xóa khỏi phiếu!')
    return redirect('dashboard:warehouse_batch_add_items', pk=batch.pk)

@admin_required
def warehouse_import_excel(request):
    from dashboard.models import Warehouse
    from dashboard.forms import ImportExcelForm
    from dashboard.utils import import_warehouse_from_excel
    
    if request.method == 'POST':
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES.get('excel_file')
            warehouse = form.cleaned_data['warehouse']
            supplier = form.cleaned_data.get('supplier', '')
            
            result = import_warehouse_from_excel(excel_file, warehouse, supplier)
            if result['success']:
                messages.success(request, f"Đã nhập {result['items_added']} sản phẩm. Phiếu: {result['batch_number']}")
                if result['errors']:
                    for error in result['errors']:
                        messages.warning(request, error)
                return redirect('dashboard:warehouse_batch_detail', pk=result['batch_id'])
            else:
                messages.error(request, f"Lỗi: {result['error']}")
    else:
        form = ImportExcelForm()
    
    return render(request, 'dashboard/warehouse/import_excel.html', {
        'form': form,
        'page_title': 'Nhập Kho Từ Excel',
    })


# ==================== SEARCH API ====================
@api_view(['GET'])
def api_search_stores(request):
    """API tìm cửa hàng theo tên hoặc địa chỉ"""
    from dashboard.utils import search_stores_by_location
    
    query = request.GET.get('q', '').strip()
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')
    radius = float(request.GET.get('radius', 5))  # km
    
    stores = Store.objects.all()
    
    # Tìm kiếm theo tên hoặc địa chỉ
    if query:
        stores = search_items(stores, query, ['name', 'address'])
    
    # Tìm kiếm theo vị trí địa lý
    if latitude and longitude:
        try:
            lat = float(latitude)
            lng = float(longitude)
            nearby = search_stores_by_location(lat, lng, radius)
            result_data = [{
                'id': item['store'].id,
                'name': item['store'].name,
                'address': item['store'].address,
                'latitude': item['store'].latitude,
                'longitude': item['store'].longitude,
                'distance': item['distance'],
                'opening_hours': item['store'].opening_hours,
            } for item in nearby]
            return Response(result_data)
        except ValueError:
            return Response({'error': 'Vĩ độ/Kinh độ không hợp lệ'}, status=400)
    
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_search_by_alley(request):
    """API tìm cửa hàng trong hẻm/con hẻm"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Vui lòng nhập từ khóa tìm kiếm'}, status=400)
    
    stores = Store.objects.all()
    results = search_items(stores, query, ['address'])
    
    serializer = StoreSerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_warehouse_low_stock(request):
    """API lấy danh sách sản phẩm tồn kho thấp"""
    from dashboard.models import WarehouseItem
    
    warehouse_id = request.GET.get('warehouse_id')
    low_stock = WarehouseItem.objects.filter(quantity__lte=models.F('min_quantity'))
    
    if warehouse_id:
        low_stock = low_stock.filter(warehouse_id=warehouse_id)
    
    data = [{
        'id': item.id,
        'product': item.product.name,
        'warehouse': item.warehouse.store.name,
        'quantity': item.quantity,
        'min_quantity': item.min_quantity,
        'unit': item.unit,
    } for item in low_stock.select_related('product', 'warehouse__store')]
    
    return Response(data)


# ==================== API (DRF) ====================
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user and request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAdminOrReadOnly]

@api_view(['GET', 'POST'])
def store_list_create(request):
    if request.method == 'GET':
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]
