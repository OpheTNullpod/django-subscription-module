from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # View available plans
    path('plans/', views.plan_list, name='plan_list'),

    # Subscribe to a selected plan
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),

    # Manage subscription - restricted to logged-in users
    path('manage/', login_required(views.manage_subscription), name='manage_subscription'),

    # Initiate PayPal payment process for a subscription
    path('paypal/start/<int:subscription_id>/', views.initiate_payment, name='start_paypal_payment'),

    # Execute PayPal payment after user approval
    path('paypal/execute/', views.execute_paypal_payment, name='execute_paypal_payment'),
]
