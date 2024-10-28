from django.test import TestCase
from django.contrib.auth.models import User
from .models import Plan, Subscription, Payment

class SubscriptionTests(TestCase):
    def setUp(self):
        """Set up test user and plan."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.plan = Plan.objects.create(name='Basic Plan', price=10.0)

    def test_subscription_creation(self):
        """Test creating a new subscription."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        self.assertEqual(subscription.status, 'inactive')

    def test_payment_creation(self):
        """Test creating a new payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(user=self.user, subscription=subscription, amount=10.0)
        self.assertEqual(payment.status, 'pending')
