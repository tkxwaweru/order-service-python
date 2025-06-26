from django.urls import path
from .views import CustomerListCreateAPIView, OrderListCreateAPIView
from .views import homepage_view

urlpatterns = [
    path('', homepage_view),
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create')
]