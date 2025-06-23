"""
Views for the API methods for each table
"""

from rest_framework import generics
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer

class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer