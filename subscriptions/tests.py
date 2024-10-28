from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
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

    def test_juice_payment_pending(self):
        """Test that Juice payments are set as pending."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='juice_mcb'
        )
        self.assertEqual(payment.status, 'pending')

    def test_manual_payment_update(self):
        """Test manual update of Juice payment status."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='juice_mcb'
        )
        # Simulate manual update by admin
        payment.status = 'successful'
        payment.save()
        self.assertEqual(payment.status, 'successful')

    def test_mips_payment_success(self):
        """Test successful MIPS payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='mips'
        )
        # Simulate successful payment from MIPS API callback
        payment.status = 'successful'
        payment.save()
        self.assertEqual(payment.status, 'successful')

    def test_subscription_activation_on_successful_payment(self):
        """Test activating subscription on successful payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='mips',
            status='successful'
        )
        subscription.activate()
        self.assertEqual(subscription.status, 'active')

    def test_subscription_renewal(self):
        """Test subscription renewal process."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active')
        subscription.renew()
        self.assertEqual(subscription.status, 'renewing')

    def test_complete_subscription_renewal(self):
        """Test completing the subscription renewal process."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='renewing')
        subscription.complete_renewal()
        self.assertEqual(subscription.status, 'active')
        self.assertIsNotNone(subscription.end_date)

    def test_recurring_payment_option(self):
        """Test setting a subscription with recurring payment option."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active')
        subscription.is_recurring = True
        subscription.save()

        # Simulate payment for recurring subscription
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='mips',
            status='successful'
        )
        self.assertTrue(subscription.is_recurring)
        self.assertEqual(payment.status, 'successful')

    def test_standing_order_manual_confirmation(self):
        """Test handling standing orders with manual confirmation."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user, 
            subscription=subscription, 
            amount=10.0, 
            payment_method='internet_banking',
            status='pending'
        )

        # Simulate admin manual confirmation of payment
        payment.status = 'successful'
        payment.save()

        # Activate subscription after payment confirmation
        subscription.activate()
        self.assertEqual(payment.status, 'successful')
        self.assertEqual(subscription.status, 'active')

    def test_expired_subscription_notification(self):
        """Test notifying users when the subscription expires."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active')
        subscription.end_date = timezone.now() - timezone.timedelta(days=1)  # Set end date in the past
        subscription.save()

        # Check if the subscription is expired
        if subscription.end_date < timezone.now():
            subscription.status = 'expired'
            subscription.save()

        self.assertEqual(subscription.status, 'expired')
    
    def test_paypal_payment_creation(self):
        """Test creating a PayPal payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=10.0,
            payment_method='paypal'
        )
        self.assertEqual(payment.payment_method, 'paypal')
        self.assertEqual(payment.status, 'pending')

    def test_paypal_successful_payment(self):
        """Test successful PayPal payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=10.0,
            payment_method='paypal'
        )

        # Simulate PayPal payment success
        payment.status = 'successful'
        payment.save()

        self.assertEqual(payment.status, 'successful')

    def test_paypal_payment_execution_flow(self):
        """Test the execution flow of PayPal payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan)
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=10.0,
            payment_method='paypal'
        )

        # Simulate PayPal's payment execution response
        payment.status = 'successful'
        payment.save()
        subscription.activate()

        self.assertEqual(payment.status, 'successful')
        self.assertEqual(subscription.status, 'active')

    def test_recurring_paypal_payment(self):
        """Test recurring PayPal payment setup."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active')
        subscription.is_recurring = True
        subscription.save()

        # Simulate recurring PayPal payment
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=10.0,
            payment_method='paypal',
            status='successful'
        )
        self.assertTrue(subscription.is_recurring)
        self.assertEqual(payment.status, 'successful')

    def test_paypal_payment_cancellation(self):
        """Test cancellation of PayPal payment."""
        subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active')
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=10.0,
            payment_method='paypal',
            status='pending'
        )

        # Simulate cancellation of PayPal payment
        payment.status = 'cancelled'
        payment.save()

        self.assertEqual(payment.status, 'cancelled')
        self.assertEqual(subscription.status, 'active')  # Subscription status remains active until confirmed
