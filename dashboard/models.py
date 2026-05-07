from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.utils import timezone

# ========== CORE MODELS ==========

# 1. Cửa Hàng
class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên cửa hàng")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ")
    latitude = models.FloatField(verbose_name="Vĩ độ")
    longitude = models.FloatField(verbose_name="Kinh độ")
    opening_hours = models.CharField(max_length=255, default="9:00 - 22:00", blank=True, verbose_name="Giờ mở cửa")
    warehouse_info = models.TextField(blank=True, verbose_name="Thông tin kho")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cửa Hàng"


# ========== HR MODELS ==========

# 2. Phòng Ban
class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên phòng ban")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Phòng Ban"


# 3. Nhân Viên
class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='employees', verbose_name="Cửa hàng")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name="Phòng ban")
    first_name = models.CharField(max_length=100, verbose_name="Tên")
    last_name = models.CharField(max_length=100, verbose_name="Họ")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    position = models.CharField(max_length=100, blank=True, verbose_name="Chức vụ")
    hire_date = models.DateField(verbose_name="Ngày tuyển dụng")
    salary = models.FloatField(default=0, verbose_name="Lương")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Nhân Viên"


# ========== CATALOG MODELS ==========

# 4. Danh Mục Sản Phẩm
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Hình ảnh")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Danh Mục"


# 5. Nhãn Hiệu
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nhãn hiệu")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Nhãn Hiệu"


# 6. Sản Phẩm / Hàng Hóa / Vật Phẩm
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Nhãn hiệu")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Mã vạch")
    cost_price = models.FloatField(verbose_name="Giá vốn")
    sale_price = models.FloatField(verbose_name="Giá bán")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho hiện tại")
    min_stock = models.IntegerField(default=10, verbose_name="Tồn kho tối thiểu")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Hình ảnh")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        """Giảm tồn kho theo số lượng chỉ định."""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    class Meta:
        verbose_name_plural = "Sản Phẩm"
        ordering = ['-created_at']

# ========== INVENTORY MODELS ==========

# 7. Kho
class Warehouse(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='warehouse', verbose_name="Cửa hàng")
    info = models.TextField(blank=True, verbose_name="Thông tin kho")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"Kho - {self.store.name}"

    class Meta:
        verbose_name_plural = "Kho"


# 8. Tồn Kho
class StockBalance(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_balances', verbose_name="Kho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_balances', verbose_name="Sản phẩm")
    quantity_on_hand = models.IntegerField(default=0, verbose_name="Tồn kho hiện tại")
    quantity_reserved = models.IntegerField(default=0, verbose_name="Tồn kho dự trữ")
    last_counted_at = models.DateTimeField(null=True, blank=True, verbose_name="Lần kiểm kho cuối")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"{self.product.name} - {self.quantity_on_hand} (Kho: {self.warehouse.store.name})"

    class Meta:
        verbose_name_plural = "Tồn Kho"
        unique_together = ('warehouse', 'product')


# 9. Chuyển Động Kho
class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
        ('adjust', 'Điều chỉnh'),
        ('return', 'Trả hàng'),
    )

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_movements', verbose_name="Kho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name="Sản phẩm")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name="Loại chuyển động")
    quantity = models.IntegerField(verbose_name="Số lượng")
    reference_id = models.CharField(max_length=100, blank=True, verbose_name="Tham chiếu")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name}"

    class Meta:
        verbose_name_plural = "Chuyển Động Kho"
        ordering = ['-created_at']


# ========== PURCHASING MODELS ==========

# 10. Nhà Cung Ứng
class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên nhà cung ứng")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Người liên hệ")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    tax_code = models.CharField(max_length=50, blank=True, verbose_name="Mã số thuế")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Nhà Cung Ứng"


# 11. Đơn Mua Hàng
class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('received', 'Đã nhận'),
        ('cancelled', 'Hủy'),
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders', verbose_name="Nhà cung ứng")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_orders', verbose_name="Cửa hàng")
    po_number = models.CharField(max_length=50, unique=True, verbose_name="Số PO")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name="Ngày giao dự kiến")
    total_amount = models.FloatField(default=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders', verbose_name="Người duyệt")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_orders', verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.po_number

    class Meta:
        verbose_name_plural = "Đơn Mua Hàng"
        ordering = ['-created_at']


# 12. Chi Tiết Đơn Mua Hàng
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn mua")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity_ordered = models.IntegerField(verbose_name="Số lượng đặt")
    unit_price = models.FloatField(verbose_name="Đơn giá")
    total_price = models.FloatField(verbose_name="Thành tiền")

    def __str__(self):
        return f"{self.product.name} - {self.quantity_ordered}"

    class Meta:
        verbose_name_plural = "Chi Tiết Đơn Mua"
        unique_together = ('purchase_order', 'product')


# 13. Phiếu Nhập Hàng
class GoodsReceipt(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
    )

    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='goods_receipt', null=True, blank=True, verbose_name="Đơn mua")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='goods_receipts', verbose_name="Nhà cung ứng")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='goods_receipts', verbose_name="Kho")
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Số phiếu nhập")
    receipt_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày nhập")
    total_amount = models.FloatField(default=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.receipt_number

    class Meta:
        verbose_name_plural = "Phiếu Nhập Hàng"
        ordering = ['-created_at']


# 14. Chi Tiết Phiếu Nhập Hàng
class GoodsReceiptItem(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items', verbose_name="Phiếu nhập")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_cost = models.FloatField(verbose_name="Đơn giá")
    total_cost = models.FloatField(verbose_name="Thành tiền")

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        verbose_name_plural = "Chi Tiết Phiếu Nhập"


# ========== CRM MODELS ==========

# 15. Nhóm Khách Hàng
class CustomerGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nhóm")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    discount_percent = models.FloatField(default=0, verbose_name="Chiết khấu (%)")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Nhóm Khách Hàng"


# 16. Khách Hàng
class Customer(models.Model):
    group = models.ForeignKey(CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers', verbose_name="Nhóm khách hàng")
    first_name = models.CharField(max_length=100, verbose_name="Tên")
    last_name = models.CharField(max_length=100, verbose_name="Họ")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    loyalty_points = models.IntegerField(default=0, verbose_name="Điểm tích lũy")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Khách Hàng"
        ordering = ['-created_at']


# ========== SALES MODELS ==========

# 17. Phương Thức Thanh Toán
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên phương thức")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Phương Thức Thanh Toán"


# 18. Đơn Hàng Bán
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
    )

    # Merged from orders app: online checkout fields
    order_id = models.CharField(max_length=50, unique=True, editable=False, blank=True, verbose_name="Mã đơn hàng online")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True, verbose_name="Người đặt (online)")
    full_name = models.CharField(max_length=200, blank=True, verbose_name="Họ tên người nhận")
    shipping_address = models.TextField(blank=True, verbose_name="Địa chỉ giao hàng")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại giao hàng")
    lat = models.FloatField(null=True, blank=True, verbose_name="Vĩ độ người dùng")
    lng = models.FloatField(null=True, blank=True, verbose_name="Kinh độ người dùng")

    # Dashboard fields: in-store sales
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True, verbose_name="Cửa hàng")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders', verbose_name="Khách hàng")
    order_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Số đơn hàng")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    total_amount = models.FloatField(default=0, verbose_name="Tổng tiền")
    discount = models.FloatField(default=0, verbose_name="Chiết khấu")
    tax_amount = models.FloatField(default=0, verbose_name="Thuế")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return self.order_id or self.order_number or f"Order #{self.pk}"

    def save(self, *args, **kwargs):
        """Tự động tạo order_id hoặc order_number nếu chưa có."""
        if not self.order_id and not self.order_number:
            import uuid
            from datetime import datetime as dt
            generated = f"ORD-{dt.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            if not self.order_id:
                self.order_id = generated
            if not self.order_number:
                self.order_number = generated
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Đơn Hàng"
        ordering = ['-created_at']


# 19. Chi Tiết Đơn Hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.FloatField(verbose_name="Đơn giá")
    total_price = models.FloatField(verbose_name="Thành tiền")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def calculated_total_price(self):
        """Tính thành tiền (merged from orders app)."""
        return self.unit_price * self.quantity

    class Meta:
        verbose_name_plural = "Chi Tiết Đơn Hàng"
        unique_together = ('order', 'product')


# 20. Thanh Toán Đơn Hàng
class OrderPayment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Chưa thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('completed', 'Đã thanh toán'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name="Đơn hàng")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Phương thức thanh toán")
    amount = models.FloatField(verbose_name="Số tiền")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name="Trạng thái")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Mã tham chiếu")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày thanh toán")
    note = models.TextField(blank=True, verbose_name="Ghi chú")

    def __str__(self):
        return f"Thanh toán {self.order.order_number}"

    class Meta:
        verbose_name_plural = "Thanh Toán"
        ordering = ['-payment_date']


# ========== WAREHOUSE MODELS (Extended) ==========

# 21. Phiếu Nhập/Xuất Kho (Batch)
class WarehouseBatch(models.Model):
    BATCH_TYPES = (
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
    )
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='batches', verbose_name="Kho")
    batch_type = models.CharField(max_length=20, choices=BATCH_TYPES, verbose_name="Loại phiếu")
    batch_number = models.CharField(max_length=50, unique=True, verbose_name="Số phiếu")
    supplier = models.CharField(max_length=255, blank=True, verbose_name="Nhà cung ứng/Người nhận")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    total_amount = models.FloatField(default=0, verbose_name="Tổng tiền")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    is_printed = models.BooleanField(default=False, verbose_name="Đã in")
    printed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian in")

    def __str__(self):
        return f"{self.batch_number} - {self.get_batch_type_display()}"

    class Meta:
        verbose_name_plural = "Phiếu Nhập/Xuất Kho"
        ordering = ['-created_at']

    def calculate_total(self):
        """Tính tổng tiền của phiếu"""
        total = sum(item.quantity * item.unit_price for item in self.items.all())
        self.total_amount = total
        return total


# 22. Chi Tiết Phiếu Nhập/Xuất Kho
class WarehouseBatchItem(models.Model):
    batch = models.ForeignKey(WarehouseBatch, on_delete=models.CASCADE, related_name='items', verbose_name="Phiếu")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.FloatField(verbose_name="Đơn giá")

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        verbose_name_plural = "Chi Tiết Phiếu Nhập/Xuất"


# ========== WAREHOUSE ITEM (from dashboard1) ==========

# 23. Sản phẩm trong kho
class WarehouseItem(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items', verbose_name="Kho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng tồn")
    unit = models.CharField(max_length=50, default="cái", verbose_name="Đơn vị")
    min_quantity = models.IntegerField(default=10, verbose_name="Tồn kho tối thiểu")
    unit_price = models.FloatField(default=0, verbose_name="Giá nhập")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit}"

    def sync_product_stock(self):
        """Cập nhật stock của Product từ tổng số lượng WarehouseItem."""
        total = WarehouseItem.objects.filter(product=self.product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        self.product.stock = total
        self.product.save(update_fields=['stock', 'updated_at'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_product_stock()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        total = WarehouseItem.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        product.stock = total
        product.save(update_fields=['stock', 'updated_at'])

    class Meta:
        verbose_name_plural = "Sản Phẩm Kho"


# 24. Giao dịch kho (nhập/xuất)
class WarehouseTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
    )

    warehouse_item = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE, related_name='transactions', verbose_name="Sản phẩm kho")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Loại giao dịch")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.FloatField(default=0, verbose_name="Đơn giá")
    supplier = models.CharField(max_length=255, blank=True, verbose_name="Nhà cung ứng")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giao dịch")

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.warehouse_item.product.name}"

    class Meta:
        verbose_name_plural = "Giao Dịch Kho"
        ordering = ['-created_at']


# ========== CONTENT MODELS (from dashboard1) ==========

# 25. Giới thiệu - Bài viết trang giới thiệu
class About(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Bản nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Lưu trữ'),
    )

    title = models.CharField(max_length=200, verbose_name="Tiêu đề bài viết")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Nội dung bài viết")
    excerpt = models.TextField(max_length=300, blank=True, verbose_name="Tóm tắt")
    featured_image = models.ImageField(upload_to='about/', null=True, blank=True, verbose_name="Hình ảnh nổi bật")
    external_link = models.URLField(blank=True, verbose_name="Liên kết bài viết bên ngoài")
    source_type = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Tự viết'),
            ('word', 'Từ Word'),
            ('external', 'Từ liên kết')
        ],
        default='manual',
        verbose_name="Nguồn bài viết"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Tác giả")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Bài viết trang giới thiệu"
        ordering = ['order', '-created_at']


# 26. Thông tin cá nhân người dùng
class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name="Người dùng")

    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Nam'),
            ('female', 'Nữ'),
            ('other', 'Khác'),
        ],
        blank=True,
        verbose_name="Giới tính"
    )

    bio = models.TextField(max_length=500, blank=True, verbose_name="Tiểu sử")
    website = models.URLField(blank=True, verbose_name="Website cá nhân")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    twitter = models.URLField(blank=True, verbose_name="Twitter")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")

    is_verified = models.BooleanField(default=False, verbose_name="Đã xác thực")
    is_premium = models.BooleanField(default=False, verbose_name="Người dùng VIP")
    loyalty_points = models.IntegerField(default=0, verbose_name="Điểm tích lũy")

    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('vi', 'Tiếng Việt'),
            ('en', 'English'),
        ],
        default='vi',
        verbose_name="Ngôn ngữ ưu tiên"
    )
    email_notifications = models.BooleanField(default=True, verbose_name="Thông báo email")
    sms_notifications = models.BooleanField(default=False, verbose_name="Thông báo SMS")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP đăng nhập cuối")

    def __str__(self):
        return f"Profile của {self.user.email}"

    class Meta:
        verbose_name = "Thông tin người dùng"
        verbose_name_plural = "Thông tin người dùng"
        ordering = ['-created_at']

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email

    @property
    def display_name(self):
        return self.user.first_name or self.user.email

    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def get_completion_percentage(self):
        fields = [
            self.phone, self.address, self.avatar, self.birth_date, self.gender,
            self.bio, self.website, self.facebook, self.instagram, self.twitter, self.linkedin
        ]
        filled_fields = sum(1 for field in fields if field)
        return round((filled_fields / len(fields)) * 100, 1)


# 27. Tin tức
class News(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Bản nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Đã lưu trữ'),
    )

    CATEGORY_CHOICES = (
        ('promotion', 'Khuyến mãi'),
        ('event', 'Sự kiện'),
        ('product', 'Sản phẩm mới'),
        ('company', 'Tin công ty'),
        ('other', 'Khác'),
    )

    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="Slug")
    summary = models.TextField(max_length=500, blank=True, verbose_name="Tóm tắt")
    content = models.TextField(verbose_name="Nội dung")
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name="Hình ảnh")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Danh mục")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    is_featured = models.BooleanField(default=False, verbose_name="Tin nổi bật")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tác giả")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xuất bản")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    meta_description = models.CharField(max_length=255, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Tin tức"
        ordering = ['-created_at']

    @property
    def is_published(self):
        return self.status == 'published'

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


# 28. Đánh giá sản phẩm
class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='reviews', verbose_name="Món trong đơn hàng")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Người dùng")
    rating = models.IntegerField(verbose_name="Điểm đánh giá", choices=[(i, f"{i} sao") for i in range(1, 6)])
    content = models.TextField(verbose_name="Nội dung đánh giá")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    admin_reply = models.TextField(blank=True, verbose_name="Phản hồi của cửa hàng")
    admin_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày phản hồi")

    class Meta:
        verbose_name_plural = "Đánh giá"
        unique_together = ['order_item', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Đánh giá #{self.id} - {self.user.email} ({self.rating} sao)"

    @property
    def is_approved(self):
        return self.status == 'approved'


# 29. Hình ảnh đánh giá
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', verbose_name="Đánh giá")
    image = models.ImageField(upload_to='reviews/', verbose_name="Hình ảnh")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")

    class Meta:
        verbose_name_plural = "Hình ảnh đánh giá"
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Ảnh đánh giá #{self.id}"


# 30. Đánh giá đơn hàng
class OrderReview(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_reviews', verbose_name="Đơn hàng")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_reviews', verbose_name="Người dùng")
    overall_rating = models.IntegerField(verbose_name="Đánh giá tổng thể", choices=[(i, f"{i} sao") for i in range(1, 6)])
    food_quality = models.IntegerField(verbose_name="Chất lượng món ăn", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    service_quality = models.IntegerField(verbose_name="Chất lượng dịch vụ", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    delivery_speed = models.IntegerField(verbose_name="Tốc độ giao hàng", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    packaging_quality = models.IntegerField(verbose_name="Chất lượng đóng gói", choices=[(i, f"{i} sao") for i in range(1, 6)], null=True, blank=True)
    content = models.TextField(verbose_name="Nội dung đánh giá", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    admin_reply = models.TextField(blank=True, verbose_name="Phản hồi của cửa hàng")
    admin_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày phản hồi")

    class Meta:
        verbose_name_plural = "Đánh giá đơn hàng"
        unique_together = ['order', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Đánh giá ĐH #{self.order.id} - {self.user.email} ({self.overall_rating} sao)"

    @property
    def is_approved(self):
        return self.status == 'approved'

    def get_average_rating(self):
        ratings = []
        if self.food_quality: ratings.append(self.food_quality)
        if self.service_quality: ratings.append(self.service_quality)
        if self.delivery_speed: ratings.append(self.delivery_speed)
        if self.packaging_quality: ratings.append(self.packaging_quality)
        if ratings:
            return sum(ratings) / len(ratings)
        return self.overall_rating