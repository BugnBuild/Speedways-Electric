from django.db import models
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce



# Create your models here.
class Maps(models.Model):
    nodes = models.IntegerField()
    stations = models.IntegerField()


class Node_details(models.Model):
    current = models.CharField(max_length=3,blank=True,null=True)
    right = models.CharField(max_length=3,blank=True,null=True)
    left = models.CharField(max_length=3,blank=True,null=True)
    straight = models.CharField(max_length=3,blank=True,null=True)
    ldist = models.IntegerField(blank=True,null=True)
    rdist = models.IntegerField(blank=True,null=True)
    sdist = models.IntegerField(blank=True,null=True)

class Short(models.Model):
    start = models.CharField(max_length=3,blank=True,null=True)
    dest = models.CharField(max_length=3,blank=True,null=True)

class Regagv(models.Model):
    agvsname = models.CharField(max_length=10,blank=True,null=True)
    agvsid = models.CharField(max_length=10,blank=True,null=True)

