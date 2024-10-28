# Generated by Django 5.1.2 on 2024-10-28 17:53

import django.db.models.deletion
import django_fsm
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', django_fsm.FSMField(choices=[('inactive', 'Inactive'), ('active', 'Active'), ('renewing', 'Renewing'), ('cancelled', 'Cancelled'), ('expired', 'Expired')], default='inactive', max_length=50)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.plan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('mips', 'MIPS'), ('internet_banking', 'Internet Banking'), ('juice_mcb', 'Juice MCB')], default='mips', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('successful', 'Successful'), ('failed', 'Failed'), ('awaiting_confirmation', 'Awaiting Confirmation')], default='pending', max_length=25)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.subscription')),
            ],
        ),
    ]