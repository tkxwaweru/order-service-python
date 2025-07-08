import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from model_bakery import baker

from apps.core.models import Customer

User = get_user_model()


@pytest.mark.django_db
class TestCustomerRegistration:

    def test_passwords_must_match(self, client):
        data = {
            "first_name": "Alice",
            "last_name": "Wanjiru",
            "username": "alice",
            "phone_number": "+254712345678",
            "password1": "secret123",
            "password2": "mismatch456",
        }
        response = client.post(reverse("register_customer"), data)
        assert response.status_code == 200
        assert "The two password fields didn’t match." in response.content.decode()

    def test_invalid_phone_format(self, client):
        data = {
            "first_name": "Bob",
            "last_name": "Odinga",
            "username": "bob",
            "phone_number": "123456",
            "password1": "secret123",
            "password2": "secret123",
        }
        response = client.post(reverse("register_customer"), data)
        assert response.status_code == 200
        assert "Enter phone number starting with 07 or +254" in response.content.decode()

    def test_valid_phone_conversion(self, client):
        data = {
            "first_name": "Carol",
            "last_name": "Njeri",
            "username": "carol",
            "phone_number": "0712345678",  # valid Kenyan format
            "password1": "secret123",
            "password2": "secret123",
        }
        response = client.post(reverse("register_customer"), data, follow=True)
        assert response.status_code == 200, response.content.decode()
        user = User.objects.get(username="carol")
        assert user.phone_number == "+254712345678"
        customer = Customer.objects.get(user=user)
        assert customer.phone_number == "+254712345678"

    def test_duplicate_username_fails(self, client):
        baker.make(User, username="johndoe")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone_number": "+254712345678",
            "password1": "secret123",
            "password2": "secret123",
        }
        response = client.post(reverse("register_customer"), data)
        assert response.status_code == 200
        assert "username" in response.content.decode().lower()
        assert "already exists" in response.content.decode().lower()

    def test_manual_registration_success(self, client):
        data = {
            "first_name": "Diana",
            "last_name": "Kamau",
            "username": "diana",
            "phone_number": "0711223344",  # valid local number
            "password1": "secret123",
            "password2": "secret123",
        }
        response = client.post(reverse("register_customer"), data, follow=True)
        assert response.status_code == 200, response.content.decode()
        assert User.objects.filter(username="diana").exists()
        user = User.objects.get(username="diana")
        assert user.phone_number == "+254711223344"
        assert Customer.objects.filter(user=user).exists()

    def test_oidc_user_registration_flow(self, client):
        """Simulates Google OIDC authenticated user completing registration."""
        oidc_user = baker.make(User, username="googleuser", phone_number="")
        client.force_login(oidc_user)

        data = {
            "first_name": "Grace",
            "last_name": "Wambui",
            "username": "googleuser",  # same username
            "phone_number": "0712345678",
            "password1": "secret123",
            "password2": "secret123",
        }

        response = client.post(reverse("register_customer"), data, follow=True)
        assert response.status_code == 200, response.content.decode()
        user = User.objects.get(username="googleuser")
        assert user.phone_number == "+254712345678"
        assert Customer.objects.filter(user=user).exists()
