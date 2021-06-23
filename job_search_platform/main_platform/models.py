from django.db import models
from django.contrib.auth.models import User
from django.db import migrations


class Company(models.Model):
    """
    All informations about a company saved by one or more users
    """
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
    headcount_text = models.CharField(max_length=30)
    contact_mode = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    alternance = models.BooleanField(null=True)
    siret = models.CharField(max_length=14, unique=True)


class RomeCode(models.Model):
    """
    Code used by the french government to identify all trades
    (needed to search companies)
    """
    code = models.CharField(max_length=5, unique=True)


class TradeToRomeCode(models.Model):
    """
    Used to associate every trade to it's rome code
    (rome codes can be linked to many trades, but 1 trade as 1 rome code)
    """
    job_name = models.CharField(max_length=200, unique=True)
    job_code = models.ForeignKey(RomeCode, on_delete=models.CASCADE)


class UserInfos(models.Model):
    """
    Associates a user to his job code and location
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=7, null=True)
    job_code = models.ForeignKey(RomeCode, on_delete=models.CASCADE, null=True)
