from django import forms
from .models import Customer, Order

ITEM_CHOICES = [
    ("Laptop", 80000),
    ("Smartphone", 45000),
    ("Headphones", 7000),
    ("Monitor", 20000),
    ("Desk Chair", 15000),
]

class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone_number']

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip().replace(" ", "")

        if phone.startswith("07") or phone.startswith("01"):
            phone = "+254" + phone[1:]  # Convert to +2547XXX or +2541XXX
        elif phone.startswith("254"):
            phone = "+" + phone
        elif not phone.startswith("+254"):
            raise forms.ValidationError("Please enter a valid Kenyan phone number.")

        return phone

class OrderForm(forms.Form):
    selected_item = forms.ChoiceField(
        choices=[(item, f"{item} - Ksh {price}") for item, price in ITEM_CHOICES],
        label="Select Item",
    )

