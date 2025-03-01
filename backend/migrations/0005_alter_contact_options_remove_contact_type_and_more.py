# Generated by Django 5.1.4 on 2025-02-17 06:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_alter_user_managers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'Контакт', 'verbose_name_plural': 'Список контактов пользователя'},
        ),
        migrations.RemoveField(
            model_name='contact',
            name='type',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='value',
        ),
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='surname',
        ),
        migrations.AddField(
            model_name='productinfo',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Внешний ID'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='city',
            field=models.CharField(blank=True, max_length=50, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$')], verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='street',
            field=models.CharField(blank=True, max_length=100, verbose_name='Улица'),
        ),
    ]
