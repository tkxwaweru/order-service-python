"""
Views for the API methods and user interface
"""

from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout, authenticate, login, get_backends
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from django.conf import settings
from django.shortcuts import render, redirect
# from django.core.management import call_command
from .models import Customer, Order, OrderItem
from .forms import CustomerRegistrationForm # OrderForm, ITEM_CHOICES
from .serializers import CustomerSerializer, OrderSerializer
from common.utils import send_order_confirmation_sms
import subprocess
from django.contrib.admin.views.decorators import staff_member_required
from apps.inventory.models import InventoryItem
from django.template.loader import render_to_string
from weasyprint import HTML
import json
from common.utils import notify_shop_employee_stock_low

class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        send_order_confirmation_sms(order)

def run_migrations_view(request):
    expected_token = getattr(settings, "MIGRATION_SECRET_TOKEN", None)
    received_token = request.headers.get("X-Migrate-Token")

    if expected_token and received_token == expected_token:
        try:
            # Apply common migration first, faked
            subprocess.run(["python", "manage.py", "migrate", "common", "0001", "--fake"], check=True)

            # Now apply all others normally
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


# @login_required
def register_customer_view(request):
    if request.user.is_authenticated:
        try:
            if request.user.customer:
                return redirect('order_form')
        except Customer.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST, initial={"user": request.user})
        if form.is_valid():
            # OIDC users: user already exists
            if request.user and request.user.is_authenticated:
                customer = form.save(user=request.user)
            else:
                customer = form.save()  # manual

            # Ensure backend is set for login
            backend = get_backends()[0]
            customer.user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, customer.user)

            return redirect('order_form')
        else:
            # ✅ Handle invalid form submission
            return render(request, 'core/register.html', {'form': form})
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
        cart_data = request.POST.get('cart_data')
        try:
            items = json.loads(cart_data)
        except (json.JSONDecodeError, TypeError):
            messages.error(request, "Invalid cart data.")
            return redirect('order_form')

        if not items:
            messages.warning(request, "Please add at least one item to your order.")
            return redirect('order_form')

        order = Order.objects.create(
            customer=customer,
            amount=0  # Temporary value to satisfy the NOT NULL constraint
        )

        total_price = 0
        sms_summary = []

        for item in items:
            try:
                inventory_item = InventoryItem.objects.get(id=item['id'])
            except InventoryItem.DoesNotExist:
                messages.error(request, f"Item ID {item['id']} not found.")
                continue

            qty = int(item['qty'])

            if inventory_item.on_hand < qty:
                messages.warning(request, f"Not enough stock for {inventory_item.name}. Available: {inventory_item.on_hand}")
                continue

            # Update inventory
            inventory_item.on_hand -= qty
            inventory_item.save()

            # ✅ NEW: Check warn limit
            if inventory_item.on_hand <= inventory_item.warn_limit:
                notify_shop_employee_stock_low(inventory_item.name, inventory_item.on_hand)

            OrderItem.objects.create(
                order=order,
                item=inventory_item,
                quantity=qty,
                price_at_order=inventory_item.price
            )

            total_price += qty * float(inventory_item.price)
            sms_summary.append(f"{inventory_item.name} x{qty}")

        if not order.items.exists():
            order.delete()
            messages.error(request, "No items could be processed. Order cancelled.")
            return redirect('order_form')

        # Save total to deprecated amount field (for compatibility)
        order.amount = total_price
        order.save()

        # Send SMS with item summary
        send_order_confirmation_sms(order, summary=", ".join(sms_summary))

        return render(request, 'core/order_success.html', {
            'order': order,
            'summary': sms_summary,
            'total_price': total_price
        })

    # GET request
    inventory_items = InventoryItem.objects.filter(on_hand__gt=0)
    return render(request, 'core/order_form.html', {
        'customer': customer,
        'inventory_items': inventory_items
    })


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
            return redirect('admin_dashboard' if user.is_staff else 'order_form')
        else:
            return render(request, 'core/home.html', {
                'show_login_error': True
            })

    return render(request, 'core/home.html')  # Normal GET

@staff_member_required
def inventory_summary_view(request):
    items = InventoryItem.objects.all()
    return render(request, 'core/inventory_summary.html', {'items': items})

@staff_member_required
def order_summary_view(request):
    orders = Order.objects.prefetch_related('items__inventory_item', 'customer')
    return render(request, 'core/order_summary.html', {'orders': orders})

@login_required
def order_receipt_pdf(request, order_id):
    order = Order.objects.get(id=order_id)

    html_string = render_to_string("core/order_receipt.html", {"order": order})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = f'filename="order_{order.id}_receipt.pdf"'
    return response

