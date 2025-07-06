from django import forms
from .models import Customer, Order
import re

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
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': '+254 XXX XXX XXX',
                'class': 'form-control',
                'id': 'phone_number',
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        phone = re.sub(r"[^\d+]", "", phone)  # remove spaces, dashes, brackets etc.

        if phone.startswith("07") or phone.startswith("01"):
            phone = "+254" + phone[1:]
        elif phone.startswith("254"):
            phone = "+" + phone
        elif not phone.startswith("+254"):
            raise forms.ValidationError("Please enter a valid Kenyan phone number.")

        # Final format validation
        if not re.match(r"^\+254\d{9}$", phone):
            raise forms.ValidationError("Phone number must be in format +2547XXXXXXXX or +2541XXXXXXXX")

        return phone

class OrderForm(forms.Form):
    selected_item = forms.ChoiceField(
        choices=[(item, f"{item} - Ksh {price}") for item, price in ITEM_CHOICES],
        label="Select Item",
    )

