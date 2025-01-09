from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)