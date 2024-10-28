from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Subscription, Payment
from django.contrib import messages
from paypalrestsdk import Payment as PayPalPayment
import paypalrestsdk
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def configure_paypal():
    """Configure the PayPal SDK."""
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,  # 'sandbox' or 'live'
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

def plan_list(request):
    """List available plans."""
    plans = Plan.objects.all()
    return render(request, 'subscriptions/plan_list.html', {'plans': plans})

def subscribe(request, plan_id):
    """Subscribe to a plan."""
    plan = get_object_or_404(Plan, id=plan_id)
    is_recurring = request.POST.get('is_recurring', False)
    subscription, created = Subscription.objects.get_or_create(user=request.user, plan=plan)

    if created:
        subscription.is_recurring = is_recurring
        subscription.activate()
        messages.success(request, f'Subscribed to {plan.name} successfully!')
    else:
        messages.info(request, f'You are already subscribed to {plan.name}.')

    return redirect('manage_subscription')

def manage_subscription(request):
    logger.debug("Entering manage_subscription view")
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user, status='active').first()
        logger.info(f"Found subscription: {subscription}")
    else:
        logger.warning("Unauthenticated user tried to access manage_subscription")
        return redirect('login')

    return render(request, 'subscriptions/manage_subscription.html', {'subscription': subscription})
def initiate_payment(request, subscription_id, payment_method):
    """Initiate a payment for a subscription."""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    amount = subscription.plan.price

    # Create a new payment instance
    payment = Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=amount,
        payment_method=payment_method
    )

    # Handle different payment methods
    if payment_method == 'paypal':
        return initiate_paypal_payment(request, payment)

    payment.process_payment()

    if payment.status == 'successful':
        messages.success(request, 'Payment successful!')
    else:
        messages.info(request, 'Payment is pending confirmation.')
        
    return redirect('manage_subscription')

def initiate_paypal_payment(request, payment):
    """Initiate PayPal payment."""
    configure_paypal()

    paypal_payment = PayPalPayment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(payment.amount),
                "currency": "USD"
            },
            "description": f"Subscription to {payment.subscription.plan.name}"
        }],
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/paypal/execute/'),
            "cancel_url": request.build_absolute_uri('/paypal/cancel/')
        }
    })

    if paypal_payment.create():
        for link in paypal_payment.links:
            if link.rel == "approval_url":
                payment.transaction_reference = paypal_payment.id
                payment.save()
                return redirect(link.href)
    else:
        logger.error(f"PayPal error: {paypal_payment.error}")
        messages.error(request, 'Error creating PayPal payment.')
        return redirect('manage_subscription')

def execute_paypal_payment(request):
    """Execute PayPal payment after user approval."""
    configure_paypal()

    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = PayPalPayment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        local_payment = Payment.objects.get(transaction_reference=payment_id)
        local_payment.status = 'successful'
        local_payment.save()
        messages.success(request, 'PayPal payment successful!')
    else:
        messages.error(request, 'Failed to complete PayPal payment.')

    return redirect('manage_subscription')
