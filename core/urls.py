from django.urls import path
from .views import home_view, CustomerListCreateAPIView, OrderListCreateAPIView, register_customer_view, order_form_view, logout_view, login_redirect_view

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_customer_view, name='register_customer'),
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('create-order/', order_form_view, name='order_form'),
    path('login-redirect/', login_redirect_view, name='login_redirect'),
    path('logout/', logout_view, name='logout')
]