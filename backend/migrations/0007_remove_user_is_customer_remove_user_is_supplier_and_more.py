# Generated by Django 5.1.4 on 2025-02-20 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_alter_productinfo_price_alter_productinfo_price_rrc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_customer',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_supplier',
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('customer', 'Customer'), ('supplier', 'Supplier'), ('admin', 'Admin')], default='customer', max_length=10, verbose_name='Роль'),
        ),
    ]
