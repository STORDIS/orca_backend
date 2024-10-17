from django.db import models


class ReDiscoveryConfig(models.Model):

    device_ip = models.CharField(max_length=64, primary_key=True)
    interval = models.IntegerField()
    last_discovered = models.DateTimeField(null=True)

    objects = models.Manager()
