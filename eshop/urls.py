from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EshopPasswordResetForm, EshopSetPasswordForm

app_name = 'eshop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<str:order_id>/', views.order_success, name='order_success'),
    path('order/payment/<str:order_id>/', views.payment_simulate, name='payment_simulate'),
    path('order/tracking/', views.order_tracking, name='order_tracking'),
    path('tim-duong/', views.directions, name='directions'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='eshop/auth/password_reset.html',
        form_class=EshopPasswordResetForm,
        email_template_name='eshop/auth/password_reset_email.html',
        success_url='/password-reset/done/',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='eshop/auth/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='eshop/auth/password_reset_confirm.html',
        form_class=EshopSetPasswordForm,
        success_url='/reset/done/',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='eshop/auth/password_reset_complete.html',
    ), name='password_reset_complete'),

    # Error pages (testable in DEBUG=True)
    path('error/<int:status_code>/', views.error_test_view, name='error_test'),
]
