from django.contrib import admin
from .models import Plan, Subscription, Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'amount', 'payment_method', 'status', 'payment_date')
    actions = ['mark_as_successful']

    def mark_as_successful(self, request, queryset):
        queryset.update(status='successful')
        for payment in queryset:
            if payment.subscription.status == 'renewing' or payment.subscription.status == 'pending_payment':
                payment.subscription.complete_renewal()

        self.message_user(request, "Selected payments marked as successful.")
    mark_as_successful.short_description = "Mark selected payments as successful"
