# Generated by Django 4.1.3 on 2023-04-04 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_subscription_psp_id_subscription_psp_reference'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
