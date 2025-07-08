from django import forms
from common.models import CustomUser
from .models import Customer
import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

ITEM_CHOICES = [
    ("Laptop", 80000),
    ("Smartphone", 45000),
    ("Headphones", 7000),
    ("Monitor", 20000),
    ("Desk Chair", 15000),
]

User = get_user_model()

class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=150)
    phone_number = forms.CharField(
    validators=[
        RegexValidator(
            regex=r'^(\+254|07)\d{8}$',
            message="Enter phone number starting with 07 or +254"
        )
    ],
    max_length=15
    )
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The two password fields didn’t match.")
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get("username")

        # If editing an existing user (OIDC), allow same username
        if self.initial.get("user") and self.initial["user"].username == username:
            return username

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists. Please choose another.")
        return username


    def clean_phone_number(self):
        number = self.cleaned_data['phone_number'].strip()
        if number.startswith("07"):
            return "+254" + number[1:]  # Convert 07XX... → +2547XX...
        elif number.startswith("+254") and len(number) == 13:
            return number
        else:
            raise forms.ValidationError("Enter phone number starting with 07 or +254")

    def save(self, user=None):
        data = self.cleaned_data
        normalized_phone = self.clean_phone_number()

        if user:
            user.username = data['username']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.phone_number = normalized_phone
            user.set_password(data['password1'])
            user.save()
        else:
            user = CustomUser.objects.create_user(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=normalized_phone,
                password=data['password1'],
            )

        customer = Customer.objects.create(
            user=user,
            name=f"{data['first_name']} {data['last_name']}",
            phone_number=normalized_phone
        )
        return customer
    
class OrderForm(forms.Form):
    selected_item = forms.ChoiceField(
        choices=[(item, f"{item} - Ksh {price}") for item, price in ITEM_CHOICES],
        label="Select Item",
    )

