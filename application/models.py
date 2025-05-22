from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Property(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    image = models.ImageField(upload_to="media/")
    reserved = models.BooleanField()
    sold = models.BooleanField()


class Agent(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    linkedin = models.CharField(max_length=100)
    num_sales = models.IntegerField(default=0)
    mail = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class AgentProperties(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

class Characteristic(models.Model):
    name = models.CharField(max_length=50)
    value = models.IntegerField()

class PropertyCharacteristics(models.Model):
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

