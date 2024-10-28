from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Subscription, Payment
from django.contrib import messages

def plan_list(request):
    """Displays available subscription plans."""
    plans = Plan.objects.all()
    return render(request, 'subscriptions/plan_list.html', {'plans': plans})

def subscribe(request, plan_id):
    """Handles subscription to a plan."""
    plan = get_object_or_404(Plan, id=plan_id)
    subscription, created = Subscription.objects.get_or_create(user=request.user, plan=plan)

    if created:
        subscription.activate()
        messages.success(request, f'Subscribed to {plan.name} successfully!')
    else:
        messages.info(request, f'You are already subscribed to {plan.name}.')

    return redirect('manage_subscription')

def manage_subscription(request):
    """Allows users to manage their subscriptions."""
    subscription = Subscription.objects.filter(user=request.user, status='active').first()
    return render(request, 'subscriptions/manage_subscription.html', {'subscription': subscription})
