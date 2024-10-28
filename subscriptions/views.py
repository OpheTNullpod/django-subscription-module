from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Subscription, Payment
from django.contrib import messages

def plan_list(request):
    """List available plans."""
    plans = Plan.objects.all()
    return render(request, 'subscriptions/plan_list.html', {'plans': plans})

def subscribe(request, plan_id):
    """Subscribe to a plan."""
    plan = get_object_or_404(Plan, id=plan_id)
    is_recurring = request.POST.get('is_recurring', False)  # Check for recurring option
    subscription, created = Subscription.objects.get_or_create(user=request.user, plan=plan)

    if created:
        subscription.is_recurring = is_recurring
        subscription.activate()
        messages.success(request, f'Subscribed to {plan.name} successfully!')
    else:
        messages.info(request, f'You are already subscribed to {plan.name}.')

    return redirect('manage_subscription')

def manage_subscription(request):
    """Manage user subscription."""
    subscription = Subscription.objects.filter(user=request.user, status='active').first()
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
    payment.process_payment()

    if payment.status == 'successful':
        messages.success(request, 'Payment successful!')
    else:
        messages.info(request, 'Payment is pending confirmation.')
        
    return redirect('manage_subscription')
