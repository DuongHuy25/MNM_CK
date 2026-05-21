from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from dashboard.models import (
    Store, Product, Order, OrderItem, Category, Warehouse, Employee, Department,
    Supplier, PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem,
    WarehouseBatch, WarehouseBatchItem, Customer, CustomerGroup, StockMovement,
    Brand, PaymentMethod, OrderPayment,
    WarehouseItem, WarehouseTransaction, About, CustomerProfile, News,
    Review, ReviewImage, ContactSettings, DiscountCode, DiscountCodeUsage
)

User = get_user_model()


INPUT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
SELECT_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
TEXTAREA_CLASS = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Tìm kiếm', widget=forms.TextInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Tìm kiếm...',
        'autocomplete': 'off',
    }))


# ========== Store Form ==========
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'latitude', 'longitude', 'opening_hours', 'warehouse_info', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên cửa hàng'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Địa chỉ chi tiết'}),
            'latitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Vĩ độ', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Kinh độ', 'step': '0.000001'}),
            'opening_hours': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '9:00 - 22:00'}),
            'warehouse_info': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Thông tin kho'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Employee Form ==========
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên phòng ban'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['store', 'department', 'first_name', 'last_name', 'email', 'phone', 'position', 'hire_date', 'salary', 'is_active']
        widgets = {
            'store': forms.Select(attrs={'class': SELECT_CLASS}),
            'department': forms.Select(attrs={'class': SELECT_CLASS}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Họ'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số điện thoại'}),
            'position': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Chức vụ'}),
            'hire_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Lương', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Category Form ==========
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên danh mục'}),
            'slug': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'slug-danh-muc'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Brand Form ==========
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên nhãn hiệu'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Product Form ==========
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'description', 'barcode', 'cost_price', 'sale_price', 'min_stock', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'brand': forms.Select(attrs={'class': SELECT_CLASS}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên sản phẩm'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'barcode': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Mã vạch'}),
            'cost_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá vốn', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá bán', 'step': '0.01'}),
            'min_stock': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tồn kho tối thiểu'}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Supplier Form ==========
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'tax_code', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên nhà cung ứng'}),
            'contact_person': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Người liên hệ'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số điện thoại'}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'tax_code': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Mã số thuế'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError('Tên nhà cung cấp phải có ít nhất 2 ký tự')
        return name.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Supplier.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and special characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10 or len(phone) > 11:
                raise forms.ValidationError('Số điện thoại không hợp lệ')
        return phone


# ========== Purchase Order Form ==========
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'store', 'po_number', 'expected_delivery_date', 'status', 'note']
        widgets = {
            'supplier': forms.Select(attrs={'class': SELECT_CLASS}),
            'store': forms.Select(attrs={'class': SELECT_CLASS}),
            'po_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số PO'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'note': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }
    
    def clean_po_number(self):
        po_number = self.cleaned_data.get('po_number')
        if not po_number:
            raise forms.ValidationError('Số PO không được để trống')
        
        # Check for duplicate PO number
        if PurchaseOrder.objects.exclude(pk=self.instance.pk).filter(po_number=po_number).exists():
            raise forms.ValidationError('Số PO này đã tồn tại')
        
        return po_number
    
    def clean_expected_delivery_date(self):
        expected_delivery_date = self.cleaned_data.get('expected_delivery_date')
        
        if expected_delivery_date and expected_delivery_date < timezone.now().date():
            raise forms.ValidationError('Ngày giao hàng dự kiến không thể trong quá khứ')
        
        return expected_delivery_date


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity_ordered', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity_ordered': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
        }


# ========== Goods Receipt Form ==========
class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['purchase_order', 'supplier', 'warehouse', 'receipt_number', 'status', 'note']
        widgets = {
            'purchase_order': forms.Select(attrs={'class': SELECT_CLASS}),
            'supplier': forms.Select(attrs={'class': SELECT_CLASS}),
            'warehouse': forms.Select(attrs={'class': SELECT_CLASS}),
            'receipt_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số phiếu nhập'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'note': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }
    
    def clean_receipt_number(self):
        receipt_number = self.cleaned_data.get('receipt_number')
        if not receipt_number:
            raise forms.ValidationError('Số phiếu nhập không được để trống')
        
        # Check for duplicate receipt number
        if GoodsReceipt.objects.exclude(pk=self.instance.pk).filter(receipt_number=receipt_number).exists():
            raise forms.ValidationError('Số phiếu nhập này đã tồn tại')
        
        return receipt_number
    
    def clean(self):
        cleaned_data = super().clean()
        purchase_order = cleaned_data.get('purchase_order')
        supplier = cleaned_data.get('supplier')
        
        # If purchase order is selected, auto-fill supplier
        if purchase_order and purchase_order.supplier:
            cleaned_data['supplier'] = purchase_order.supplier
        
        # Validate that either purchase order or supplier is selected
        if not purchase_order and not supplier:
            raise forms.ValidationError('Phải chọn đơn mua hàng hoặc nhà cung cấp')
        
        return cleaned_data


class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        fields = ['product', 'quantity', 'unit_cost']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_cost': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
        }


# ========== Customer Form ==========
class CustomerGroupForm(forms.ModelForm):
    class Meta:
        model = CustomerGroup
        fields = ['name', 'description', 'discount_percent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên nhóm khách hàng'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'discount_percent': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Chiết khấu (%)', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['group', 'first_name', 'last_name', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'group': forms.Select(attrs={'class': SELECT_CLASS}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Họ'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Order Form ==========
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['store', 'customer', 'order_number', 'status', 'discount', 'note']
        widgets = {
            'store': forms.Select(attrs={'class': SELECT_CLASS}),
            'customer': forms.Select(attrs={'class': SELECT_CLASS}),
            'order_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số đơn hàng'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'discount': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Chiết khấu', 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
        }


# ========== Warehouse Batch Form ==========
class WarehouseBatchForm(forms.ModelForm):
    class Meta:
        model = WarehouseBatch
        fields = ['warehouse', 'batch_type', 'batch_number', 'supplier', 'description']
        widgets = {
            'warehouse': forms.Select(attrs={'class': SELECT_CLASS}),
            'batch_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'batch_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số phiếu'}),
            'supplier': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung ứng/Người nhận'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }


class WarehouseBatchItemForm(forms.ModelForm):
    class Meta:
        model = WarehouseBatchItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Để trống nếu không đổi mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Họ'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên'}),
            'role': forms.Select(attrs={'class': SELECT_CLASS}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (but allow the same email for the current user when editing)
            if self.instance and self.instance.pk:
                # Editing: exclude current user from uniqueness check
                if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Email này đã được đăng ký.')
            else:
                # Creating: check if email exists
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError('Email này đã được đăng ký.')
        return email


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['store', 'info']
        widgets = {
            'store': forms.Select(attrs={'class': SELECT_CLASS}),
            'info': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 8, 'placeholder': 'Nhập thông tin quản lý kho...'}),
        }


class ImportExcelForm(forms.Form):
    """Form để tải lên file Excel import kho"""
    excel_file = forms.FileField(
        label='Tệp Excel',
        widget=forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': '.xlsx,.xls,.csv'})
    )
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label='Kho hàng',
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    supplier = forms.CharField(
        max_length=255,
        label='Nhà cung cấp',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung cấp'}),
        required=False
    )


class StoreSearchForm(forms.Form):
    """Form tìm kiếm cửa hàng theo tên hoặc địa chỉ"""
    query = forms.CharField(
        max_length=255,
        required=False,
        label='Tìm cửa hàng',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Tìm kiếm theo tên hoặc địa chỉ...'
        })
    )
    latitude = forms.FloatField(
        required=False,
        label='Vĩ độ',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Vĩ độ (tùy chọn)',
            'step': '0.000001'
        })
    )
    longitude = forms.FloatField(
        required=False,
        label='Kinh độ',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Kinh độ (tùy chọn)',
            'step': '0.000001'
        })
    )


# ========== Warehouse Item Form (from dashboard1) ==========
class WarehouseItemForm(forms.ModelForm):
    class Meta:
        model = WarehouseItem
        fields = ['warehouse', 'product', 'quantity', 'unit', 'min_quantity', 'unit_price']
        widgets = {
            'warehouse': forms.Select(attrs={'class': SELECT_CLASS}),
            'product': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng tồn'}),
            'unit': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'cái, kg, lít...'}),
            'min_quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tồn kho tối thiểu'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá nhập', 'step': '0.01'}),
        }


class WarehouseTransactionForm(forms.ModelForm):
    class Meta:
        model = WarehouseTransaction
        fields = ['warehouse_item', 'transaction_type', 'quantity', 'unit_price', 'supplier', 'note']
        widgets = {
            'warehouse_item': forms.Select(attrs={'class': SELECT_CLASS}),
            'transaction_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Số lượng'}),
            'unit_price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Đơn giá', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhà cung cấp'}),
            'note': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Ghi chú'}),
        }


# ========== About Forms (from dashboard1) ==========
class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = ['title', 'slug', 'content', 'excerpt', 'featured_image', 'external_link', 'source_type', 'status', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tiêu đề bài viết'}),
            'slug': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'slug-tieu-de-bai-viet'}),
            'content': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 10, 'placeholder': 'Nội dung chi tiết bài viết...'}),
            'excerpt': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Tóm tắt ngắn gọn...'}),
            'featured_image': forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'external_link': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com/bai-viet'}),
            'source_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '0', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['slug'].required = True


class AboutImportForm(forms.Form):
    import_type = forms.ChoiceField(
        choices=[('word', 'Từ file Word (.docx)'), ('external', 'Từ liên kết URL')],
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
        label='Loại nhập'
    )
    word_file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': '.docx,.doc'}), label='File Word')
    external_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com/bai-viet'}), label='URL bài viết')

    def clean(self):
        cleaned_data = super().clean()
        import_type = cleaned_data.get('import_type')
        word_file = cleaned_data.get('word_file')
        external_url = cleaned_data.get('external_url')
        if import_type == 'word' and not word_file:
            raise forms.ValidationError('Vui lòng chọn file Word khi nhập từ file.')
        elif import_type == 'external' and not external_url:
            raise forms.ValidationError('Vui lòng nhập URL khi nhập từ liên kết.')
        return cleaned_data


# ========== Customer Profile Forms (from dashboard1) ==========
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = [
            'phone', 'address', 'avatar', 'birth_date', 'gender',
            'bio', 'website', 'facebook', 'instagram', 'twitter', 'linkedin',
            'preferred_language', 'email_notifications', 'sms_notifications'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập số điện thoại'}),
            'address': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Nhập địa chỉ'}),
            'avatar': forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'birth_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'gender': forms.Select(attrs={'class': SELECT_CLASS}),
            'bio': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Tiểu sử...'}),
            'website': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://website.com'}),
            'facebook': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://facebook.com/username'}),
            'instagram': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://instagram.com/username'}),
            'twitter': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://twitter.com/username'}),
            'linkedin': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://linkedin.com/in/username'}),
            'preferred_language': forms.Select(attrs={'class': SELECT_CLASS}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['phone', 'address', 'avatar', 'birth_date', 'gender', 'bio', 'website', 'facebook', 'instagram', 'twitter', 'linkedin']:
            self.fields[field_name].required = False


class UserBasicInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập tên'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập họ'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = True


# ========== News Form (from dashboard1) ==========
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'slug', 'summary', 'content', 'image', 'category', 'status', 'is_featured', 'published_at', 'meta_description', 'meta_keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nhập tiêu đề tin tức'}),
            'slug': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'slug-tin-tuc'}),
            'summary': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Tóm tắt ngắn gọn'}),
            'content': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 10, 'placeholder': 'Nội dung chi tiết'}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600'}),
            'published_at': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'meta_description': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Mô tả SEO'}),
            'meta_keywords': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Từ khóa SEO'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['summary', 'image', 'published_at', 'meta_description', 'meta_keywords']:
            self.fields[field_name].required = False


# ========== Review Forms (from dashboard1) ==========
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-radio'}),
            'content': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4, 'placeholder': 'Chia sẻ trải nghiệm...'}),
        }


class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
        }


class ReviewReplyForm(forms.Form):
    admin_reply = forms.CharField(
        widget=forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3, 'placeholder': 'Nhập phản hồi cho người dùng...'}),
        label='Phản hồi của cửa hàng',
        required=True
    )


class ContactSettingsForm(forms.ModelForm):
    class Meta:
        model = ContactSettings
        fields = ['site_name', 'intro_text', 'email', 'phone', 'address', 'working_hours',
                  'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_use_tls']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'ZenMart'}),
            'intro_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Lời giới thiệu trang liên hệ'}),
            'email': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Mỗi dòng 1 email\nvd: example@gmail.com'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '1900-xxxx'}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Địa chỉ'}),
            'working_hours': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '8:00 - 22:00'}),
            'smtp_host': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'smtp.gmail.com'}),
            'smtp_port': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '587'}),
            'smtp_user': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'email@gmail.com'}),
            'smtp_password': forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': 'App Password'}, render_value=True),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


# ========== Discount Code Form ==========
class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = [
            'code', 'name', 'description', 'discount_type', 'discount_value',
            'minimum_order_amount', 'maximum_discount_amount', 'usage_limit', 'user_limit',
            'start_date', 'end_date', 'status', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Mã giảm giá (VD: SAVE20)'}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Tên mã giảm giá'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'discount_value': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá trị giảm', 'step': '0.01'}),
            'minimum_order_amount': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giá trị đơn hàng tối thiểu', 'step': '0.01'}),
            'maximum_discount_amount': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giảm giá tối đa (tùy chọn)', 'step': '0.01'}),
            'usage_limit': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giới hạn số lần sử dụng'}),
            'user_limit': forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Giới hạn mỗi user'}),
            'start_date': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError('Mã giảm giá không được để trống')
        
        # Convert to uppercase and remove spaces
        code = code.upper().replace(' ', '')
        
        # Check for duplicate code
        if DiscountCode.objects.exclude(pk=self.instance.pk).filter(code=code).exists():
            raise forms.ValidationError('Mã giảm giá này đã tồn tại')
        
        return code
    
    def clean_discount_value(self):
        discount_value = self.cleaned_data.get('discount_value')
        discount_type = self.cleaned_data.get('discount_type')
        
        if discount_value <= 0:
            raise forms.ValidationError('Giá trị giảm phải lớn hơn 0')
        
        if discount_type == 'percentage' and discount_value > 100:
            raise forms.ValidationError('Giảm giá theo phần trăm không thể vượt quá 100%')
        
        return discount_value
    
    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('Ngày kết thúc phải sau ngày bắt đầu')
        
        return end_date
    
    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        maximum_discount_amount = cleaned_data.get('maximum_discount_amount')
        
        if discount_type == 'fixed' and maximum_discount_amount:
            raise forms.ValidationError('Giảm giá tối đa chỉ áp dụng cho loại giảm giá theo phần trăm')
        
        return cleaned_data
