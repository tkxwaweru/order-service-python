"""
Views for the API methods and user interface
"""

from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.management import call_command
from .models import Customer, Order
from .forms import CustomerRegistrationForm, OrderForm, ITEM_CHOICES
from .serializers import CustomerSerializer, OrderSerializer
from .utils import send_order_sms
import subprocess


# ------------------ API Views ------------------

class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        # Using test number for now: will change to actual customer phone number
        phone_number = "+254712345678"
        message = f"Hi {order.customer.name}, your order for '{order.item}' (Ksh {order.amount}) has been received."
        send_order_sms(phone_number, message)


# ------------------ UI Views ------------------

def run_migrations_view(request):
    expected_token = getattr(settings, "MIGRATION_SECRET_TOKEN", None)
    received_token = request.headers.get("X-Migrate-Token")

    if expected_token and received_token == expected_token:
        try:
            subprocess.run(["python", "manage.py", "migrate"], check=True)
            return HttpResponse("Migrations applied successfully.")
        except subprocess.CalledProcessError:
            return HttpResponse("Migration failed.", status=500)
    else:
        return HttpResponseForbidden("Invalid or missing migration token.")

def home_view(request):
    return render(request, 'core/home.html')

@login_required
def login_redirect_view(request):
    try:
        if request.user.customer:
            return redirect('order_form')
    except Customer.DoesNotExist:
        return redirect('register_customer')


@login_required
def register_customer_view(request):
    try:
        if request.user.customer:
            return redirect('order_form')
    except Customer.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect('order_form')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'core/register.html', {'form': form})


@login_required
def order_form_view(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return redirect('register_customer')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            selected_item = form.cleaned_data['selected_item']
            amount = dict(ITEM_CHOICES)[selected_item]

            # Create order
            order = Order.objects.create(
                customer=customer,
                item=selected_item,
                amount=amount
            )

            # Send SMS
            message = f"Hi {customer.name}, your order for '{selected_item}' (Ksh {amount}) has been received."
            send_order_sms(customer.phone_number, message)

            return render(request, 'core/order_success.html', {'order': order})
    else:
        form = OrderForm()

    return render(request, 'core/order_form.html', {'form': form, 'customer': customer})


def logout_view(request):
    logout(request)
    return redirect('home')
