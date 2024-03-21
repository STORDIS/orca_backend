from django.db import models


class Logs(models.Model):
    timestamp = models.CharField(max_length=64)
    request_json = models.JSONField()
    status = models.CharField(max_length=32)
    processing_time = models.CharField(max_length=32)
    status_code = models.IntegerField()
    response = models.JSONField()
    http_method = models.CharField(max_length=32)

    objects = models.Manager()
