from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=160, null=True, blank=True)

    def __str__(self):
        return self.username


class Site(models.Model):
    name = models.CharField(max_length=300, verbose_name="Site name")
    url = models.URLField(max_length=500, verbose_name="URL")
    protocol_security = models.BooleanField(default=True)
    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class UserStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.ForeignKey(Site, on_delete=models.CASCADE)
    page_transitions = models.IntegerField(default=0)
    data_sent = models.FloatField(default=0)
    data_received = models.FloatField(default=0)

    def __str__(self):
        return f'{self.website}'
