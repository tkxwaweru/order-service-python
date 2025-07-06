from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Customer, Order

class CustomerFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.user.save()
        """
        self.customer = baker.make(
            user = "xyz"
            name = "name" 
            code = "123"
            phone_number = "002873849"
        )

        self.customer = 

        do for all...
        """  

    def test_registration_view_access(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('register_customer'))
        self.assertEqual(response.status_code, 200)

    def test_register_customer_and_create_order(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.post(reverse('register_customer'), {
            'name': 'Test User',
            'phone_number': '0712345678'
        })
        self.assertRedirects(response, reverse('order_form'))
        self.assertTrue(Customer.objects.filter(user=self.user).exists())

        # bake the user model
        # bake the customer

       
        customer = Customer.objects.get(user=self.user)
        response = self.client.post(reverse('order_form'), {
            'selected_item': 'Laptop'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.filter(customer=customer).count(), 1)
