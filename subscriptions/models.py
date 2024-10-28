from django.conf import settings
from django.db import models
from django_fsm import FSMField, transition
from django.utils import timezone
from django.contrib.auth import get_user_model

# Get user model dynamically
User = get_user_model()

# Define payment methods and statuses
PAYMENT_METHODS = (
    ('mips', 'MIPS'),
    ('internet_banking', 'Internet Banking'),
    ('juice_mcb', 'Juice MCB'),
    ('standing_order', 'Standing Order'),
    ('paypal', 'PayPal'),
)

PAYMENT_STATUSES = (
    ('pending', 'Pending'),
    ('successful', 'Successful'),
    ('failed', 'Failed'),
    ('awaiting_confirmation', 'Awaiting Confirmation'),
)

SUBSCRIPTION_STATUSES = (
    ('inactive', 'Inactive'),
    ('active', 'Active'),
    ('renewing', 'Renewing'),
    ('cancelled', 'Cancelled'),
    ('expired', 'Expired'),
)

class Plan(models.Model):
    """Defines subscription plans."""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    """Tracks user subscriptions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = FSMField(default='inactive', choices=SUBSCRIPTION_STATUSES)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)  # Recurring payment option

    @transition(field=status, source='inactive', target='active')
    def activate(self):
        """Activates the subscription."""
        self.start_date = timezone.now()
        self.end_date = self.start_date + timezone.timedelta(days=30)
        self.save()

    @transition(field=status, source='active', target='renewing')
    def renew(self):
        """Prepare subscription renewal."""
        if self.is_recurring:
            self.complete_renewal()
        else:
            self.status = 'pending_payment'
        self.save()

    @transition(field=status, source='renewing', target='active')
    def complete_renewal(self):
        """Complete the renewal and update the end date."""
        self.end_date = timezone.now() + timezone.timedelta(days=30)
        self.save()

class Payment(models.Model):
    """Handles payments for subscriptions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paypal')
    status = models.CharField(max_length=25, choices=PAYMENT_STATUSES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_method} - {self.status}"

    def process_payment(self):
        """Processes the payment based on the selected method."""
        if self.payment_method == 'mips' or self.payment_method == 'internet_banking':
            # Assume success for automated payment methods like MIPS
            self.status = 'successful'
            self.subscription.complete_renewal()
        elif self.payment_method == 'juice_mcb' or self.payment_method == 'standing_order':
            # Set as pending and require admin confirmation
            self.status = 'pending'
        self.save()
