# Generated by Django 5.1.4 on 2025-02-16 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='surname',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
