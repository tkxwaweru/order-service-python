from django.urls import path
from .views import CustomerListCreateAPIView, OrderListCreateAPIView

urlpatterns = [
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
]