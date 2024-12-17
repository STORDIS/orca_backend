from django.db import models


# Create your models here.

class DHCPServerDetails(models.Model):
    device_ip = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=64)
    ssh_access = models.BooleanField(default=False)

    objects = models.Manager()
