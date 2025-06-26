"""
Views for the API methods for each table
"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from core.utils import send_order_sms

from rest_framework import generics
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer

class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()

        # TEMP: hardcoded phone number (change later to pull from Customer or request)
        phone_number = "+254712345678"  # Use the test number from Africa's Talking
        message = f"Hi {order.customer.name}, your order for '{order.item}' (Ksh {order.amount}) has been received."

        send_order_sms(phone_number, message)

@login_required
def homepage_view(request):
    return HttpResponse(f"Welcome, {request.user.username} — you're logged in via Google!")
