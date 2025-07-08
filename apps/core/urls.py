from django.urls import path
from .views import order_receipt_pdf, inventory_summary_view, order_summary_view, manual_login_view, admin_dashboard_view
from .views import run_migrations_view, home_view, CustomerListCreateAPIView, OrderListCreateAPIView 
from .views import  register_customer_view, order_form_view, logout_view, login_redirect_view

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_customer_view, name='register_customer'),
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('create-order/', order_form_view, name='order_form'),
    path('login-redirect/', login_redirect_view, name='login_redirect'),
    path("run-migrations/", run_migrations_view, name="run_migrations"),
    path('manual-login/', manual_login_view, name='manual_login'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/inventory/', inventory_summary_view, name='inventory_summary'),
    path('dashboard/orders/', order_summary_view, name='order_summary'),
    path('orders/<int:order_id>/receipt/', order_receipt_pdf, name='order_receipt_pdf'),
]