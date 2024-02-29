from django.db import models

# Create your models here.


class Logs(models.Model):

    timestamp = models.CharField(max_length=64)
    request_json = models.JSONField()
    status = models.CharField(max_length=32)
    processing_time = models.CharField(max_length=32)

    objects = models.Manager()
