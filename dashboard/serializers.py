from rest_framework import serializers
from .models import (
    Store, Department, Employee, Category, Brand, Product,
    Warehouse, WarehouseItem, WarehouseTransaction,
    StockBalance, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem,
    GoodsReceipt, GoodsReceiptItem, CustomerGroup, Customer, PaymentMethod, Order,
    OrderItem, OrderPayment, WarehouseBatch, WarehouseBatchItem,
    About, CustomerProfile, News, Review, ReviewImage, OrderReview
)


# ========== CORE SERIALIZERS ==========

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'opening_hours', 'warehouse_info', 'is_active', 'created_at', 'updated_at']


# ========== HR SERIALIZERS ==========

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'store', 'store_name', 'department', 'department_name', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'position', 'hire_date', 'salary', 'is_active', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ========== CATALOG SERIALIZERS ==========

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'is_active', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'brand', 'brand_name', 'name', 'description', 'barcode', 'cost_price', 'sale_price', 'min_stock', 'image', 'is_active', 'created_at', 'updated_at']


# ========== INVENTORY SERIALIZERS ==========

class WarehouseSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'store', 'store_name', 'info', 'created_at', 'updated_at']


class StockBalanceSerializer(serializers.ModelSerializer):
    warehouse_store_name = serializers.CharField(source='warehouse.store.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockBalance
        fields = ['id', 'warehouse', 'warehouse_store_name', 'product', 'product_name', 'quantity_on_hand', 'quantity_reserved', 'last_counted_at', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    warehouse_store_name = serializers.CharField(source='warehouse.store.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'warehouse', 'warehouse_store_name', 'product', 'product_name', 'movement_type', 'quantity', 'reference_id', 'note', 'created_by', 'created_by_name', 'created_at']


# ========== PURCHASING SERIALIZERS ==========

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'tax_code', 'is_active', 'created_at', 'updated_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'purchase_order', 'product', 'product_name', 'quantity_ordered', 'unit_price', 'total_price']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'supplier_name', 'store', 'store_name', 'po_number', 'order_date', 'expected_delivery_date', 'total_amount', 'status', 'note', 'approved_by', 'created_by', 'items', 'created_at', 'updated_at']


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = GoodsReceiptItem
        fields = ['id', 'goods_receipt', 'product', 'product_name', 'quantity', 'unit_cost', 'total_cost']


class GoodsReceiptSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_store_name = serializers.CharField(source='warehouse.store.name', read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = ['id', 'purchase_order', 'supplier', 'supplier_name', 'warehouse', 'warehouse_store_name', 'receipt_number', 'receipt_date', 'total_amount', 'status', 'note', 'created_by', 'items', 'created_at', 'updated_at']


# ========== CRM SERIALIZERS ==========

class CustomerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerGroup
        fields = ['id', 'name', 'description', 'discount_percent', 'is_active']


class CustomerSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'group', 'group_name', 'first_name', 'last_name', 'full_name', 'phone', 'email', 'address', 'loyalty_points', 'is_active', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ========== SALES SERIALIZERS ==========

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description', 'is_active']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'store', 'store_name', 'customer', 'customer_name', 'order_number', 'order_date', 'status', 'total_amount', 'discount', 'tax_amount', 'note', 'created_by', 'items', 'created_at', 'updated_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)

    class Meta:
        model = OrderPayment
        fields = ['id', 'order', 'order_number', 'payment_method', 'payment_method_name', 'amount', 'status', 'reference_number', 'payment_date', 'note']


# ========== WAREHOUSE BATCH SERIALIZERS ==========

class WarehouseBatchItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = WarehouseBatchItem
        fields = ['id', 'batch', 'product', 'product_name', 'quantity', 'unit_price']


class WarehouseBatchSerializer(serializers.ModelSerializer):
    items = WarehouseBatchItemSerializer(many=True, read_only=True)
    warehouse_store_name = serializers.CharField(source='warehouse.store.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = WarehouseBatch
        fields = ['id', 'warehouse', 'warehouse_store_name', 'batch_type', 'batch_number', 'supplier', 'description', 'total_amount', 'created_by', 'created_by_name', 'is_printed', 'printed_at', 'items', 'created_at', 'updated_at']


# ========== WAREHOUSE ITEM & TRANSACTION SERIALIZERS (from dashboard1) ==========

class WarehouseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_store_name = serializers.CharField(source='warehouse.store.name', read_only=True)

    class Meta:
        model = WarehouseItem
        fields = ['id', 'warehouse', 'warehouse_store_name', 'product', 'product_name', 'quantity', 'min_quantity', 'unit_price', 'is_active', 'created_at', 'updated_at']


class WarehouseTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='warehouse_item.product.name', read_only=True)

    class Meta:
        model = WarehouseTransaction
        fields = ['id', 'warehouse_item', 'product_name', 'transaction_type', 'quantity', 'note', 'created_at']


# ========== CONTENT MANAGEMENT SERIALIZERS (from dashboard1) ==========

class AboutSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = About
        fields = ['id', 'title', 'slug', 'summary', 'content', 'image', 'status', 'is_active', 'order', 'source_type', 'external_link', 'author', 'author_name', 'created_at', 'updated_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'user_email', 'display_name', 'avatar', 'phone', 'address', 'gender', 'date_of_birth', 'is_verified', 'is_premium', 'loyalty_points', 'created_at', 'updated_at']


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'summary', 'content', 'image', 'status', 'is_featured', 'category', 'author', 'author_name', 'views_count', 'published_at', 'created_at', 'updated_at']


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'uploaded_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    product_name = serializers.CharField(source='order_item.product.name', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'order_item', 'user', 'user_name', 'product_name', 'rating', 'content', 'status', 'admin_reply', 'admin_reply_at', 'images', 'created_at', 'updated_at']


class OrderReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = OrderReview
        fields = ['id', 'order', 'order_id', 'user', 'user_name', 'overall_rating', 'food_quality', 'service_quality', 'delivery_speed', 'packaging_quality', 'content', 'status', 'admin_reply', 'admin_reply_at', 'created_at', 'updated_at']


# ========== CHECKOUT SERIALIZERS (merged from orders app) ==========

class CheckoutOrderItemSerializer(serializers.Serializer):
    """Serializer cho từng item trong đơn hàng checkout online."""
    product_id = serializers.IntegerField(min_value=1, help_text="ID sản phẩm")
    quantity = serializers.IntegerField(min_value=1, help_text="Số lượng đặt")

    def validate_product_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Product ID phải là số dương.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải là số dương.")
        return value


class CheckoutSerializer(serializers.Serializer):
    """Serializer cho quá trình checkout online."""
    shipping_address = serializers.CharField(max_length=500, required=True, help_text="Địa chỉ giao hàng")
    phone_number = serializers.CharField(max_length=20, required=True, help_text="Số điện thoại liên hệ")
    note = serializers.CharField(max_length=1000, required=False, allow_blank=True, help_text="Ghi chú đơn hàng")
    items = CheckoutOrderItemSerializer(many=True, required=True, min_length=1, help_text="Danh sách sản phẩm đặt")

    def validate_phone_number(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Số điện thoại phải có ít nhất 10 ký tự.")
        return value.strip()

    def validate_shipping_address(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Địa chỉ giao hàng phải có ít nhất 10 ký tự.")
        return value.strip()

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Phải có ít nhất 1 sản phẩm trong đơn hàng.")
        product_ids = [item.get('product_id') for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Trùng product_id trong đơn hàng.")
        return value

    def validate(self, attrs):
        total_quantity = sum(item['quantity'] for item in attrs['items'])
        if total_quantity > 100:
            raise serializers.ValidationError("Tổng số lượng không được vượt quá 100 mỗi đơn.")
        return attrs
