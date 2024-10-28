from django.conf import settings
from django.db import models
from django_fsm import FSMField, transition
from django.utils import timezone

# Payment options available to users
PAYMENT_METHODS = (
    ('mips', 'MIPS'),
    ('internet_banking', 'Internet Banking'),
    ('juice_mcb', 'Juice MCB'),
)

# Status options for payment transactions
PAYMENT_STATUSES = (
    ('pending', 'Pending'),
    ('successful', 'Successful'),
    ('failed', 'Failed'),
    ('awaiting_confirmation', 'Awaiting Confirmation'),
)

# Different states a subscription can have
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
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Plan price
    description = models.TextField(blank=True)  # Additional description

    def __str__(self):
        return self.name  # Returns the name of the plan

class Subscription(models.Model):
    """Tracks user subscriptions to different plans."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = FSMField(default='inactive', choices=SUBSCRIPTION_STATUSES)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    @transition(field=status, source='inactive', target='active')
    def activate(self):
        """Activates the subscription and sets start/end dates."""
        self.start_date = timezone.now()
        self.end_date = self.start_date + timezone.timedelta(days=30)
        self.save()

    @transition(field=status, source='active', target='renewing')
    def renew(self):
        """Prepares subscription for renewal."""
        pass

    @transition(field=status, source='renewing', target='active')
    def complete_renewal(self):
        """Completes the renewal process and updates the end date."""
        self.end_date = timezone.now() + timezone.timedelta(days=30)
        self.save()

class Payment(models.Model):
    """Handles payments related to subscriptions."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mips')
    status = models.CharField(max_length=25, choices=PAYMENT_STATUSES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_method} - {self.status}"
