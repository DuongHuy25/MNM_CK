from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Email',
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Mật khẩu',
        }),
        label='Mật khẩu'
    )

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            user = authenticate(request=None, username=email, password=password)
            if user is None:
                raise forms.ValidationError('Email hoặc mật khẩu không đúng.')
            if not user.is_active:
                raise forms.ValidationError('Tài khoản đã bị vô hiệu hóa.')
        return cleaned


class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Email',
        }),
        label='Email'
    )
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Họ và tên',
        }),
        label='Họ tên'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Số điện thoại (tùy chọn)',
        }),
        label='Số điện thoại'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Mật khẩu (ít nhất 6 ký tự)',
        }),
        label='Mật khẩu',
        min_length=6,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Nhập lại mật khẩu',
        }),
        label='Xác nhận mật khẩu'
    )

    def clean_email(self):
        from users.models import User
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email đã được sử dụng.')
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password2')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('Mật khẩu không khớp.')
        return cleaned


class EshopPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Nhập email đã đăng ký',
        }),
        label='Email'
    )


class EshopSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Mật khẩu mới',
        }),
        label='Mật khẩu mới'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Nhập lại mật khẩu mới',
        }),
        label='Xác nhận mật khẩu mới'
    )


class ProfileEditForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Họ và tên',
        }),
        label='Họ tên'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Số điện thoại',
        }),
        label='Số điện thoại'
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'eshop-input',
            'placeholder': 'Địa chỉ giao hàng mặc định',
            'rows': 3,
        }),
        label='Địa chỉ'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'eshop-input',
            'accept': 'image/*',
        }),
        label='Ảnh đại diện'
    )


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Họ và tên người nhận',
        }),
        label='Họ tên'
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Số điện thoại liên hệ',
        }),
        label='Số điện thoại'
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'eshop-input',
            'placeholder': 'Địa chỉ giao hàng',
            'rows': 3,
        }),
        label='Địa chỉ giao hàng'
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'eshop-input',
            'placeholder': 'Ghi chú (tùy chọn)',
            'rows': 2,
        }),
        label='Ghi chú'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Thanh toán khi nhận hàng (COD)'),
            ('bank', 'Chuyển khoản ngân hàng'),
            ('momo', 'Ví MoMo'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'eshop-radio',
        }),
        label='Phương thức thanh toán'
    )


class OrderTrackingForm(forms.Form):
    order_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'eshop-input',
            'placeholder': 'Nhập mã đơn hàng (VD: ORD-20250507-A1B2C3D4)',
        }),
        label='Mã đơn hàng'
    )
