from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products',   views.ProductViewSet,  basename='product')
router.register(r'stores',     views.StoreViewSet,    basename='store')
router.register(r'categories', views.CategoryViewSet, basename='category')

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Stores
    path('stores/',                views.stores_list,   name='stores_list'),
    path('stores/create/',         views.stores_create, name='stores_create'),
    path('stores/<int:pk>/',       views.stores_detail, name='stores_detail'),
    path('stores/<int:pk>/edit/',  views.stores_edit,   name='stores_edit'),
    path('stores/<int:pk>/delete/',views.stores_delete, name='stores_delete'),

    # Employees
    path('employees/',                views.employees_list,   name='employees_list'),
    path('employees/create/',         views.employees_create, name='employees_create'),
    path('employees/<int:pk>/',       views.employees_detail, name='employees_detail'),
    path('employees/<int:pk>/edit/',  views.employees_edit,   name='employees_edit'),
    path('employees/<int:pk>/delete/',views.employees_delete, name='employees_delete'),

    # Categories
    path('categories/',                views.categories_list,   name='categories_list'),
    path('categories/create/',         views.categories_create, name='categories_create'),
    path('categories/<int:pk>/edit/',  views.categories_edit,   name='categories_edit'),
    path('categories/<int:pk>/delete/',views.categories_delete, name='categories_delete'),

    # Brands
    path('brands/',                   views.brands_list,   name='brands_list'),
    path('brands/create/',          views.brands_create, name='brands_create'),
    path('brands/<int:pk>/',        views.brands_detail, name='brands_detail'),
    path('brands/<int:pk>/edit/',   views.brands_edit,   name='brands_edit'),
    path('brands/<int:pk>/delete/', views.brands_delete, name='brands_delete'),

    # Products

    path('products/',                views.products_list,   name='products_list'),
    path('products/create/',         views.products_create, name='products_create'),
    path('products/<int:pk>/',       views.products_detail, name='products_detail'),
    path('products/<int:pk>/edit/',  views.products_edit,   name='products_edit'),
    path('products/<int:pk>/delete/',views.products_delete, name='products_delete'),

    # Customers (offline - keep for backward compat)
    path('customers/',                views.customers_list,   name='customers_list'),
    path('customers/create/',         views.customers_create, name='customers_create'),
    path('customers/<int:pk>/edit/',  views.customers_edit,   name='customers_edit'),
    path('customers/<int:pk>/delete/',views.customers_delete, name='customers_delete'),

    # Unified Customers (merged: Users + CustomerProfile + Customers)
    path('khach-hang/',                          views.customers_unified_list,               name='customers_unified_list'),
    path('khach-hang/create/',                   views.customers_unified_create,             name='customers_unified_create'),
    path('khach-hang/<int:pk>/',                 views.customers_unified_detail,             name='customers_unified_detail'),
    path('khach-hang/<int:pk>/edit/',            views.customers_unified_edit,               name='customers_unified_edit'),
    path('khach-hang/<int:pk>/delete/',          views.customers_unified_delete,             name='customers_unified_delete'),
    path('khach-hang/<int:pk>/toggle-verification/', views.customers_unified_toggle_verification, name='customers_unified_toggle_verification'),

    # Orders
    path('orders/',                views.orders_list,   name='orders_list'),
    path('orders/create/',         views.orders_create, name='orders_create'),
    path('orders/<int:pk>/',       views.orders_detail, name='orders_detail'),
    path('orders/<int:pk>/edit/',  views.orders_edit,   name='orders_edit'),
    path('orders/<int:pk>/delete/',views.orders_delete, name='orders_delete'),

    # Users (from dashboard1)
    path('users/',                views.users_list,   name='users_list'),
    path('users/create/',         views.users_create, name='users_create'),
    path('users/<int:pk>/',       views.users_detail, name='users_detail'),
    path('users/<int:pk>/edit/',  views.users_edit,   name='users_edit'),
    path('users/<int:pk>/delete/',views.users_delete, name='users_delete'),

    # Warehouse
    path('warehouse/',                     views.warehouse_list,            name='warehouse_list'),
    path('warehouse/<int:pk>/',            views.warehouse_detail,          name='warehouse_detail'),
    path('warehouse/create/',              views.warehouse_create,          name='warehouse_create'),
    path('warehouse/<int:pk>/edit/',       views.warehouse_edit,            name='warehouse_edit'),
    path('warehouse/<int:pk>/delete/',     views.warehouse_delete,          name='warehouse_delete'),

    # Warehouse Item
    path('warehouse-item/create/',         views.warehouse_item_create,     name='warehouse_item_create'),
    path('warehouse-item/<int:pk>/edit/',  views.warehouse_item_edit,       name='warehouse_item_edit'),
    path('warehouse-item/<int:pk>/delete/',views.warehouse_item_delete,     name='warehouse_item_delete'),

    # Warehouse Transaction
    path('warehouse-transaction/create/',      views.warehouse_transaction_create,  name='warehouse_transaction_create'),
    path('warehouse-transaction/<int:pk>/delete/', views.warehouse_transaction_delete, name='warehouse_transaction_delete'),

    # Warehouse Batch
    path('warehouse-batch/',                           views.warehouse_batch_list,        name='warehouse_batch_list'),
    path('warehouse-batch/create/',                    views.warehouse_batch_create,      name='warehouse_batch_create'),
    path('warehouse-batch/template-excel/<int:warehouse_id>/', views.warehouse_batch_template_excel, name='warehouse_batch_template_excel'),
    path('warehouse-batch/<int:pk>/add-items/',        views.warehouse_batch_add_items,   name='warehouse_batch_add_items'),
    path('warehouse-batch/<int:pk>/',                  views.warehouse_batch_detail,      name='warehouse_batch_detail'),
    path('warehouse-batch/<int:pk>/print/',            views.warehouse_batch_print,       name='warehouse_batch_print'),
    path('warehouse-batch/<int:pk>/export-excel/',     views.warehouse_batch_export_excel, name='warehouse_batch_export_excel'),
    path('warehouse-batch/<int:pk>/delete/',           views.warehouse_batch_delete,      name='warehouse_batch_delete'),
    path('warehouse-batch-item/<int:pk>/delete/',      views.warehouse_batch_item_delete, name='warehouse_batch_item_delete'),
    path('warehouse/import-excel/',                    views.warehouse_import_excel,      name='warehouse_import_excel'),

    # About Management
    path('about/', views.about_list, name='about_list'),
    path('about/create/', views.about_create, name='about_create'),
    path('about/<int:pk>/', views.about_detail, name='about_detail'),
    path('about/<int:pk>/edit/', views.about_edit, name='about_edit'),
    path('about/<int:pk>/delete/', views.about_delete, name='about_delete'),
    path('about/import/', views.about_import, name='about_import'),

    # Customer Profile Management
    path('customer-profiles/', views.customer_profile_list, name='customer_profile_list'),
    path('customer-profiles/<int:pk>/', views.customer_profile_detail, name='customer_profile_detail'),
    path('customer-profiles/<int:pk>/edit/', views.customer_profile_edit, name='customer_profile_edit'),
    path('customer-profiles/<int:pk>/delete/', views.customer_profile_delete, name='customer_profile_delete'),
    path('customer-profiles/<int:pk>/toggle-verification/', views.customer_profile_toggle_verification, name='customer_profile_toggle_verification'),

    # News Management
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('news/<int:pk>/toggle-status/', views.news_toggle_status, name='news_toggle_status'),
    path('news/<int:pk>/toggle-featured/', views.news_toggle_featured, name='news_toggle_featured'),

    # Review Management
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('reviews/<int:pk>/approve/', views.review_approve, name='review_approve'),
    path('reviews/<int:pk>/reject/', views.review_reject, name='review_reject'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),

    # Order Review Management
    path('order-reviews/', views.order_review_list, name='order_review_list'),
    path('order-reviews/<int:pk>/', views.order_review_detail, name='order_review_detail'),
    path('order-reviews/<int:pk>/approve/', views.order_review_approve, name='order_review_approve'),
    path('order-reviews/<int:pk>/reject/', views.order_review_reject, name='order_review_reject'),
    path('order-reviews/<int:pk>/delete/', views.order_review_delete, name='order_review_delete'),

    # Search & API
    path('api/search/stores/',     views.api_search_stores,       name='api_search_stores'),
    path('api/search/alley/',      views.api_search_by_alley,     name='api_search_alley'),
    path('api/warehouse/low-stock/', views.api_warehouse_low_stock, name='api_low_stock'),

    # API endpoints for new CRUD views
    path('api/suppliers/', views.supplier_list_api, name='api_suppliers'),
    path('api/purchase-orders/', views.purchase_order_list_api, name='api_purchase_orders'),
    path('api/goods-receipts/', views.goods_receipt_list_api, name='api_goods_receipts'),
    path('api/customer-groups/', views.customer_group_list_api, name='api_customer_groups'),
    path('api/stock-balances/', views.stock_balance_list_api, name='api_stock_balances'),
    path('api/stock-movements/', views.stock_movement_list_api, name='api_stock_movements'),

    # REST Framework
    path('api/', include(router.urls)),
    path('api/stores-create/', views.store_list_create, name='store_api'),

    # Manage stores
    path('manage/', views.manage_stores_view, name='manage_stores'),

    # Contact Settings
    path('contact-settings/', views.contact_settings, name='contact_settings'),

    # Supplier Management
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Purchase Order Management
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/edit/', views.purchase_order_edit, name='purchase_order_edit'),
    path('purchase-orders/<int:pk>/confirm/', views.purchase_order_confirm, name='purchase_order_confirm'),
    path('purchase-orders/<int:pk>/cancel/', views.purchase_order_cancel, name='purchase_order_cancel'),
    path('purchase-orders/<int:pk>/delete/', views.purchase_order_delete, name='purchase_order_delete'),

    # Goods Receipt Management
    path('goods-receipts/', views.goods_receipt_list, name='goods_receipt_list'),
    path('goods-receipts/create/', views.goods_receipt_create, name='goods_receipt_create'),
    path('goods-receipts/<int:pk>/', views.goods_receipt_detail, name='goods_receipt_detail'),
    path('goods-receipts/<int:pk>/edit/', views.goods_receipt_edit, name='goods_receipt_edit'),
    path('goods-receipts/<int:pk>/confirm/', views.goods_receipt_confirm, name='goods_receipt_confirm'),
    path('goods-receipts/<int:pk>/cancel/', views.goods_receipt_cancel, name='goods_receipt_cancel'),
    path('goods-receipts/<int:pk>/delete/', views.goods_receipt_delete, name='goods_receipt_delete'),

    # Customer Group Management
    path('customer-groups/', views.customer_group_list, name='customer_group_list'),
    path('customer-groups/create/', views.customer_group_create, name='customer_group_create'),
    path('customer-groups/<int:pk>/', views.customer_group_detail, name='customer_group_detail'),
    path('customer-groups/<int:pk>/edit/', views.customer_group_edit, name='customer_group_edit'),
    path('customer-groups/<int:pk>/delete/', views.customer_group_delete, name='customer_group_delete'),

    # Stock Management
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),
    path('stock-balances/', views.stock_balance_list, name='stock_balance_list'),
    path('stock-balances/<int:pk>/', views.stock_balance_detail, name='stock_balance_detail'),

    # Report Export
    path('export/orders-excel/', views.export_orders_excel, name='export_orders_excel'),
    path('export/revenue-excel/', views.export_revenue_excel, name='export_revenue_excel'),
    path('export/stock-excel/', views.export_stock_excel, name='export_stock_excel'),

    # Discount Code Management
    path('discount-codes/', views.discount_code_list, name='discount_code_list'),
    path('discount-codes/create/', views.discount_code_create, name='discount_code_create'),
    path('discount-codes/<int:pk>/', views.discount_code_detail, name='discount_code_detail'),
    path('discount-codes/<int:pk>/edit/', views.discount_code_edit, name='discount_code_edit'),
    path('discount-codes/<int:pk>/delete/', views.discount_code_delete, name='discount_code_delete'),

    # Discount Code API
    path('api/discount-codes/validate/', views.validate_discount_code, name='validate_discount_code'),

    # Checkout API (merged from orders app)
    path('api/checkout/',          views.CheckoutAPIView.as_view(), name='checkout'),
    path('api/orders/',            views.order_list_view,           name='api_order_list'),
    path('api/orders/<str:order_id>/', views.order_detail_view,     name='api_order_detail'),
]
