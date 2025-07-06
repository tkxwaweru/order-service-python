"""
Views for the API methods and user interface
"""

from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.management import call_command
from .models import Customer, Order
from .forms import CustomerRegistrationForm, OrderForm, ITEM_CHOICES
from .serializers import CustomerSerializer, OrderSerializer
from common.utils import send_order_confirmation_sms
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
        send_order_confirmation_sms(order)


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
    if request.user.is_staff:
        return HttpResponseForbidden("Admins are not allowed to place orders.")

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
            send_order_confirmation_sms(order)

            return render(request, 'core/order_success.html', {'order': order})
    else:
        form = OrderForm()

    return render(request, 'core/order_form.html', {'form': form, 'customer': customer})



def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def admin_dashboard_view(request):
    # You can render a simple template that shows stock/orders, etc.
    return render(request, 'core/admin_dashboard.html')

def manual_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')  # Replace with actual admin interface
            else:
                return redirect('order_form')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return redirect('home')  # fallback
