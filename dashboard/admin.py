from django.contrib import admin
from dashboard.models import (
    Store, Department, Employee, Category, Brand, Product,
    Warehouse, WarehouseItem, WarehouseTransaction,
    StockBalance, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem,
    GoodsReceipt, GoodsReceiptItem, CustomerGroup, Customer, PaymentMethod, Order,
    OrderItem, OrderPayment, WarehouseBatch, WarehouseBatchItem,
    About, CustomerProfile, News, Review, ReviewImage, OrderReview
)


# ========== CORE ADMIN ==========

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'opening_hours', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'address')
    fieldsets = (
        ('Thông Tin Cơ Bản', {
            'fields': ('name', 'address', 'opening_hours')
        }),
        ('Vị Trí', {
            'fields': ('latitude', 'longitude')
        }),
        ('Kho', {
            'fields': ('warehouse_info',)
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )


# ========== HR ADMIN ==========

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'store', 'department', 'position', 'hire_date', 'is_active')
    list_filter = ('is_active', 'store', 'department', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    fieldsets = (
        ('Thông Tin Cá Nhân', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Công Việc', {
            'fields': ('store', 'department', 'position', 'hire_date', 'salary')
        }),
        ('Tài Khoản', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Họ Tên'


# ========== CATALOG ADMIN ==========

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'cost_price', 'sale_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'brand', 'created_at')
    search_fields = ('name', 'barcode')
    fieldsets = (
        ('Thông Tin Sản Phẩm', {
            'fields': ('name', 'description', 'category', 'brand')
        }),
        ('Giá Cả', {
            'fields': ('cost_price', 'sale_price')
        }),
        ('Kho', {
            'fields': ('barcode', 'min_stock', 'image')
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )


# ========== INVENTORY ADMIN ==========

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('store', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('store__name',)


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity_on_hand', 'quantity_reserved')
    list_filter = ('warehouse', 'updated_at')
    search_fields = ('product__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'movement_type', 'quantity', 'created_at')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('product__name', 'reference_id')
    readonly_fields = ('created_at',)


# ========== PURCHASING ADMIN ==========

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    fieldsets = (
        ('Thông Tin Nhà Cung Ứng', {
            'fields': ('name', 'contact_person', 'email', 'phone', 'address', 'tax_code')
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'store', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'store', 'created_at')
    search_fields = ('po_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'supplier', 'warehouse', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'warehouse', 'created_at')
    search_fields = ('receipt_number', 'supplier__name')
    inlines = [GoodsReceiptItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


# ========== CRM ADMIN ==========

@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'group', 'loyalty_points', 'is_active', 'created_at')
    list_filter = ('is_active', 'group', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    fieldsets = (
        ('Thông Tin Cá Nhân', {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'address')
        }),
        ('Nhóm & Điểm', {
            'fields': ('group', 'loyalty_points')
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Họ Tên'


# ========== SALES ADMIN ==========

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'store', 'customer', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'store', 'created_at')
    search_fields = ('order_number', 'customer__first_name', 'customer__last_name')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 1


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('order__order_number',)
    readonly_fields = ('payment_date',)


# ========== WAREHOUSE BATCH ADMIN ==========

class WarehouseBatchItemInline(admin.TabularInline):
    model = WarehouseBatchItem
    extra = 1


@admin.register(WarehouseBatch)
class WarehouseBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'warehouse', 'batch_type', 'total_amount', 'is_printed', 'created_at')
    list_filter = ('batch_type', 'warehouse', 'is_printed', 'created_at')
    search_fields = ('batch_number', 'supplier')
    inlines = [WarehouseBatchItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


# ========== WAREHOUSE ITEM & TRANSACTION (from dashboard1) ==========

@admin.register(WarehouseItem)
class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'min_quantity', 'unit_price')
    list_filter = ('warehouse',)
    search_fields = ('product__name', 'warehouse__store__name')
    readonly_fields = ('updated_at',)


@admin.register(WarehouseTransaction)
class WarehouseTransactionAdmin(admin.ModelAdmin):
    list_display = ('warehouse_item', 'transaction_type', 'quantity', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('warehouse_item__product__name',)
    readonly_fields = ('created_at',)


# ========== CONTENT MANAGEMENT (from dashboard1) ==========

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'is_active', 'order', 'created_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'slug', 'content', 'summary', 'image')
        }),
        ('Phân loại', {
            'fields': ('status', 'is_active', 'order', 'author')
        }),
        ('Nguồn', {
            'fields': ('source_type', 'external_link'),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'phone', 'is_verified', 'is_premium', 'created_at')
    list_filter = ('is_verified', 'is_premium', 'gender', 'created_at')
    search_fields = ('user__email', 'user__username', 'display_name', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'loyalty_points')
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('user', 'display_name', 'avatar', 'gender', 'date_of_birth')
        }),
        ('Liên hệ', {
            'fields': ('phone', 'address')
        }),
        ('Trạng thái', {
            'fields': ('is_verified', 'is_premium', 'loyalty_points')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'is_featured', 'category', 'author', 'published_at', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'slug', 'summary', 'content', 'image', 'category')
        }),
        ('Trạng thái', {
            'fields': ('status', 'is_featured', 'author', 'published_at')
        }),
        ('Thống kê', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('order_item__product__name', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReviewImageInline]
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order_item', 'user', 'rating')
        }),
        ('Nội dung', {
            'fields': ('content',)
        }),
        ('Trạng thái', {
            'fields': ('status',)
        }),
        ('Phản hồi', {
            'fields': ('admin_reply', 'admin_reply_at')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order_item', 'user', 'order_item__product')


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('review__id',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review')


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'overall_rating', 'status', 'created_at')
    list_filter = ('status', 'overall_rating', 'created_at')
    search_fields = ('order__id', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order', 'user', 'overall_rating')
        }),
        ('Đánh giá chi tiết', {
            'fields': ('food_quality', 'service_quality', 'delivery_speed', 'packaging_quality')
        }),
        ('Nội dung', {
            'fields': ('content',)
        }),
        ('Trạng thái', {
            'fields': ('status',)
        }),
        ('Phản hồi', {
            'fields': ('admin_reply', 'admin_reply_at')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'user')
